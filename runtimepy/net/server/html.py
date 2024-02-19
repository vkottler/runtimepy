"""
A module implementing HTML interfaces for web applications.
"""

# built-in
from typing import Awaitable, Callable, Optional, TextIO

# third-party
from svgen.element import Element
from svgen.element.html import Html
from vcorelib import DEFAULT_ENCODING

# internal
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader
from runtimepy.net.tcp.http import HttpConnection

HtmlApp = Callable[
    [Html, RequestHeader, ResponseHeader, Optional[bytes]], Awaitable[None]
]
HtmlApps = dict[str, HtmlApp]


async def default_html_app(
    document: Html,
    request: RequestHeader,
    response: ResponseHeader,
    request_data: Optional[bytes],
) -> None:
    """A simple 'Hello, world!' application."""

    del request
    del response
    del request_data

    document.body.children.append(Element(tag="div", text="Hello, world!"))


async def html_handler(
    apps: HtmlApps,
    stream: TextIO,
    request: RequestHeader,
    response: ResponseHeader,
    request_data: Optional[bytes],
    default_app: HtmlApp = default_html_app,
) -> None:
    """Render an HTML document in response to an HTTP request."""

    # Set response headers.
    response["Content-Type"] = f"text/html; charset={DEFAULT_ENCODING}"

    # Create the application.
    document = Html(HttpConnection.identity)
    await apps.get(request.target.path, default_app)(
        document, request, response, request_data
    )

    stream.write("<!DOCTYPE html>\n")
    document.encode(stream)
