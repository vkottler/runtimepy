"""
A module implementing HTML interfaces for web applications.
"""

# built-in
from typing import Awaitable, Callable, Optional, TextIO

# third-party
from svgen.element.html import Html
from vcorelib import DEFAULT_ENCODING

# internal
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader
from runtimepy.net.tcp.http import HttpConnection

HtmlApp = Callable[
    [Html, RequestHeader, ResponseHeader, Optional[bytes]], Awaitable[Html]
]
HtmlApps = dict[str, HtmlApp]


async def html_handler(
    apps: HtmlApps,
    stream: TextIO,
    request: RequestHeader,
    response: ResponseHeader,
    request_data: Optional[bytes],
    default_app: HtmlApp = None,
) -> None:
    """Render an HTML document in response to an HTTP request."""

    # Set response headers.
    response["Content-Type"] = f"text/html; charset={DEFAULT_ENCODING}"

    # Create the application.
    app = apps.get(request.target.path, default_app)
    if app is not None:
        (
            await app(
                Html(HttpConnection.identity), request, response, request_data
            )
        ).render(stream)
