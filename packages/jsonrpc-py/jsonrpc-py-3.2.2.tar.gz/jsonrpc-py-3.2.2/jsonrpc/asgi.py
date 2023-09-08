import re
from asyncio import CancelledError, Task, create_task, shield
from collections import UserDict
from collections.abc import Generator, MutableSequence
from http import HTTPMethod, HTTPStatus
from io import DEFAULT_BUFFER_SIZE, BytesIO
from typing import Any, ClassVar, Final, Generic, TypeAlias, TypeVar

from .dispatcher import AsyncDispatcher
from .errors import Error
from .lifespan import LifespanEvents, LifespanManager
from .requests import BatchRequest, Request
from .responses import BatchResponse, Response
from .serializers import JSONSerializer
from .typedefs import ASGIReceiveCallable, ASGISendCallable, HTTPConnectionScope, Scope
from .utilities import CancellableGather

__all__: Final[tuple[str, ...]] = ("ASGIHandler",)

KT = TypeVar("KT")
VT = TypeVar("VT")


class ASGIHandler(UserDict[KT, VT], Generic[KT, VT]):
    """
    Base class representing the ``ASGI`` entry point.
    Its subclassing the :py:class:`collections.UserDict` object
    for providing the user-defined data storage.

    For example::

        >>> app = ASGIHandler()
        >>> app["my_private_key"] = "foobar"
        >>> app["my_private_key"]
        "foobar"
    """

    __slots__: tuple[str, ...] = ()

    #: The default content type of the responses.
    content_type: ClassVar[str] = "application/json"

    #: Class variable representing the :class:`jsonrpc.AsyncDispatcher` object
    #: used by this class for routing user-defined functions by default.
    dispatcher: Final[AsyncDispatcher] = AsyncDispatcher()

    #: Class variable representing the :class:`jsonrpc.JSONSerializer` object
    #: used by this class for data serialization by default.
    serializer: Final[JSONSerializer] = JSONSerializer()

    #: Class variable representing the :class:`jsonrpc.LifespanEvents` object
    #: used by this class for storing the user-defined functions that running
    #: when application is initiated and shutting down.
    events: Final[LifespanEvents] = LifespanEvents()

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self.data!r})"

    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        match scope:
            case {"type": "http", **kwargs}:  # noqa: F841
                await HTTPHandler(scope, receive, send, self.__class__)  # type: ignore[arg-type]
            case {"type": "lifespan", **kwargs}:  # noqa: F841
                await LifespanManager(receive, send, self.events)
            case _:
                raise ValueError("Only ASGI/HTTP connections are allowed.")


#: ---
#: Useful typing aliases, such as too generic objects.
AnyASGIHandler: TypeAlias = ASGIHandler[Any, Any]
AnyTask: TypeAlias = Task[Any]
AnyRequest: TypeAlias = Request | Error | BatchRequest
AnyResponse: TypeAlias = Response | BatchResponse | None

#: ---
#: Ensure that "Content-Type" is a valid JSON header.
JSON_CTYPE_REGEXB: Final[re.Pattern[bytes]] = re.compile(
    rb"(?:application/|[\w.-]+/[\w.+-]+?\+)json$",
    flags=re.IGNORECASE,
)


class RequestAborted(Exception):
    """
    The request was closed before it was completed, or timed out.
    """


class HTTPException(Exception):
    __slots__: tuple[str, ...] = ("status",)

    def __init__(self, *, status: HTTPStatus) -> None:
        self.status: Final[HTTPStatus] = status


class HTTPHandler:
    """
    Main HTTP endpoint.
    """

    __slots__: tuple[str, ...] = ("scope", "receive", "send", "app")

    #: ---
    #: Avoid a "fire-and-forget" background tasks disappearing mid-execution:
    background_tasks: Final[set[AnyTask]] = set()

    def __init__(
        self,
        scope: HTTPConnectionScope,
        receive: ASGIReceiveCallable,
        send: ASGISendCallable,
        app: type[AnyASGIHandler],
    ) -> None:
        self.scope: Final[HTTPConnectionScope] = scope
        self.receive: Final[ASGIReceiveCallable] = receive
        self.send: Final[ASGISendCallable] = send
        self.app: type[AnyASGIHandler] = app

    def __await__(self) -> Generator[Any, None, None]:
        #: ---
        #: Create a suitable iterator by calling __await__ on a coroutine.
        return self.__await_impl__().__await__()

    async def __await_impl__(self) -> None:
        try:
            #: ---
            #: Might be "405 Method Not Allowed" or "415 Unsupported Media Type".
            self.negotiate_content()

            #: ---
            #: Might be "400 Bad Request" or abort.
            try:
                payload: bytes = await self.read_request_body()
            except RequestAborted:
                return
            if not payload:
                raise HTTPException(status=HTTPStatus.BAD_REQUEST)

            #: ---
            #: Should be "200 OK" or "204 No Content".
            if not (payload := await self.parse_payload(payload)):
                await self.send_response(status=HTTPStatus.NO_CONTENT)
            else:
                await self.send_response(payload=payload)

        #: ---
        #: Should be sent as is.
        except HTTPException as exc:
            await self.send_response(status=exc.status)
        #: ---
        #: Must be "504 Gateway Timeout" only.
        except (TimeoutError, CancelledError):
            await self.send_response(status=HTTPStatus.GATEWAY_TIMEOUT)

    def negotiate_content(self) -> None:
        if self.scope["method"] != HTTPMethod.POST:
            raise HTTPException(status=HTTPStatus.METHOD_NOT_ALLOWED)
        for key, value in self.scope["headers"]:
            if key == b"content-type" and not JSON_CTYPE_REGEXB.match(value):
                raise HTTPException(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    async def read_request_body(self) -> bytes:
        with BytesIO() as raw_buffer:
            while True:
                match await self.receive():
                    case {"type": "http.request", **kwargs}:
                        raw_buffer.write(kwargs.get("body", b""))  # type: ignore[arg-type]
                        if not kwargs.get("more_body", False):
                            break
                    case {"type": "http.disconnect"}:
                        raise RequestAborted("Client was disconnected too early.")

            return raw_buffer.getvalue()

    async def send_response(
        self,
        *,
        status: HTTPStatus = HTTPStatus.OK,
        payload: bytes = b"",
        buffer_size: int = DEFAULT_BUFFER_SIZE,
    ) -> None:
        headers: list[tuple[bytes, bytes]] = [
            (b"content-type", self.app.content_type.encode("ascii")),
        ]
        if status == HTTPStatus.METHOD_NOT_ALLOWED:
            headers.append((b"allow", HTTPMethod.POST.encode("ascii")))
            headers.sort()
        #: ---
        #: Initial response message:
        await self.send({"type": "http.response.start", "status": status, "headers": headers})
        #: ---
        #: Yield chunks of response:
        with BytesIO(payload) as raw_buffer:
            try:
                while chunk := raw_buffer.read(buffer_size):
                    await self.send({"type": "http.response.body", "body": chunk, "more_body": True})
            finally:
                #: ---
                #: Final closing message:
                await self.send({"type": "http.response.body", "body": b"", "more_body": False})

    async def parse_payload(self, payload: bytes) -> bytes:
        def write_error(error: Error) -> bytes:
            response: Response = Response(error=error, response_id=None)
            return self.app.serializer.serialize(response.json)

        try:
            obj: Any = self.app.serializer.deserialize(payload)
        except Error as error:
            return write_error(error)

        is_batch_request: bool = isinstance(obj, MutableSequence) and len(obj) >= 1
        request: AnyRequest = (BatchRequest if is_batch_request else Request).from_json(obj)  # type: ignore[attr-defined]

        if not (response := await self.process_request(request)):
            return b""

        try:
            return self.app.serializer.serialize(response.json)
        except Error as error:
            return write_error(error)

    async def process_request(self, obj: AnyRequest) -> AnyResponse:
        def on_error(error: Error) -> Response:
            return Response(error=error, response_id=None)

        async def on_request(request: Request) -> Response | None:
            #: ---
            #: Add task to the set. This creates a strong reference.
            self.background_tasks.add(
                task := create_task(
                    self.app.dispatcher.dispatch(
                        request.method,
                        *request.args,
                        **request.kwargs,
                    )
                )
            )
            #: ---
            #: To prevent keeping references to finished tasks forever,
            #: make each task remove its own reference from the set after
            #: completion:
            task.add_done_callback(self.background_tasks.discard)
            if request.is_notification:
                #: ---
                #: Mark exception retrieved:
                task.add_done_callback(lambda task: task.cancelled() or task.exception() is None)
                return None
            try:
                result: Any = await shield(task)
                return Response(body=result, response_id=request.request_id)
            except Error as error:
                return Response(error=error, response_id=request.request_id)

        async def on_batch_request(request: BatchRequest) -> BatchResponse:
            responses: tuple[AnyResponse, ...] = await CancellableGather(map(self.process_request, request))
            return BatchResponse([response for response in responses if isinstance(response, Response)])

        if isinstance(obj, Error):
            return on_error(obj)
        elif isinstance(obj, Request):
            return await on_request(obj)
        else:
            return await on_batch_request(obj)
