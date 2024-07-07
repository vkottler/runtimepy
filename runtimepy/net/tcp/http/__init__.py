"""
A module implementing a basic HTTP (multiple RFC's) connection interface.
"""

# built-in
import asyncio
from copy import copy
import http
from json import loads
from typing import Any, Awaitable, Callable, Optional, Tuple, Union

# third-party
from vcorelib import DEFAULT_ENCODING

# internal
from runtimepy import PKG_NAME, VERSION
from runtimepy.net.http import HttpMessageProcessor
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader
from runtimepy.net.tcp.connection import TcpConnection as _TcpConnection

#
# async def handler(
#     response: ResponseHeader,
#     request: RequestHeader,
#     request_data: Optional[bytes],
# ) -> Optional[bytes]:
#     """Sample handler."""
#
HttpRequestHandler = Callable[
    [ResponseHeader, RequestHeader, Optional[bytes]],
    Awaitable[Optional[bytes]],
]
HttpResponse = Tuple[ResponseHeader, Optional[bytes]]

HttpRequestHandlers = dict[http.HTTPMethod, HttpRequestHandler]


def to_json(response: HttpResponse) -> Any:
    """Get JSON data from an HTTP response."""

    # Make sure the response is JSON.
    header = response[0]
    assert header["content-type"].startswith("application/json"), header[
        "content-type"
    ]

    return loads(
        response[1].decode(encoding=DEFAULT_ENCODING),  # type: ignore
    )


class HttpConnection(_TcpConnection):
    """A class implementing a basic HTTP interface."""

    identity = f"{PKG_NAME}/{VERSION}"

    expecting_response: bool

    log_alias = "HTTP"
    log_prefix = "http://"

    # Handlers registered at the class level so that instances created at
    # runtime don't need additional initialization.
    handlers: HttpRequestHandlers = {}

    def init(self) -> None:
        """Initialize this instance."""

        # Incoming request handling.
        self.processor = HttpMessageProcessor()

        # Outgoing request handling.
        self.request_ready = asyncio.BoundedSemaphore()
        self.expecting_response = False
        self.responses: asyncio.Queue[HttpResponse] = asyncio.Queue(maxsize=1)

        self.handlers = copy(self.handlers)
        self.handlers[http.HTTPMethod.GET] = self.get_handler
        self.handlers[http.HTTPMethod.POST] = self.post_handler

    async def get_handler(
        self,
        response: ResponseHeader,
        request: RequestHeader,
        request_data: Optional[bytes],
    ) -> Optional[bytes]:
        """Sample handler."""

    async def post_handler(
        self,
        response: ResponseHeader,
        request: RequestHeader,
        request_data: Optional[bytes],
    ) -> Optional[bytes]:
        """Sample handler."""

    async def _process_request(
        self,
        response: ResponseHeader,
        request_header: RequestHeader,
        request_data: Optional[bytes] = None,
    ) -> Optional[bytes]:
        """Process an individual request."""

        result = None

        # Handle request.
        if request_header.method in self.handlers:
            result = await self.handlers[request_header.method](
                response, request_header, request_data
            )

        # Set error code in response.
        else:
            response.status = http.HTTPStatus.NOT_IMPLEMENTED
            response.reason = (
                f"No handler for {request_header.method} requests."
            )

        # Set boilerplate header data.
        response["server"] = self.identity

        return result

    async def request(
        self, request: RequestHeader, data: Optional[bytes] = None
    ) -> HttpResponse:
        """Make an HTTP request."""

        async with self.request_ready:
            # Set boilerplate header data.
            request["user-agent"] = self.identity

            self._send(request, data)
            self.expecting_response = True
            result = await self.responses.get()
            self.expecting_response = False

        return result

    async def request_json(
        self, request: RequestHeader, data: Optional[bytes] = None
    ) -> Any:
        """
        Perform a request and convert the response to a data structure by
        decoding it as JSON.
        """
        return to_json(await self.request(request, data))

    def _send(
        self,
        header: Union[ResponseHeader, RequestHeader],
        data: Optional[bytes] = None,
    ) -> None:
        """Send a request or response to a request."""

        # Set content length.
        header["content-length"] = "0"
        if data:
            header["content-length"] = str(len(data))

        self.send_binary(bytes(header))
        if data:
            self.send_binary(data)

        header.log(self.logger, True)

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""

        kind = RequestHeader if not self.expecting_response else ResponseHeader

        for header, payload in self.processor.ingest(  # type: ignore
            data,
            kind,  # type: ignore
        ):
            header.log(self.logger, False)

            if not self.expecting_response:
                # Process request.
                response = ResponseHeader()
                self._send(
                    response,
                    await self._process_request(response, header, payload),
                )

            # Process the response to a pending request.
            else:
                await self.responses.put((header, payload))

        return True
