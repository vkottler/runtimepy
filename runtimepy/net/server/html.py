"""
A module implementing HTML interfaces for web applications.
"""

# built-in
from typing import Awaitable, Callable, Optional, TextIO

# third-party
from svgen.attribute import attributes
from svgen.element import Element
from vcorelib import DEFAULT_ENCODING

# internal
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader
from runtimepy.net.tcp.http import HttpConnection

HtmlApp = Callable[
    [Element, Element, RequestHeader, ResponseHeader, Optional[bytes]],
    Awaitable[None],
]
HtmlApps = dict[str, HtmlApp]


async def default_html_app(
    head: Element,
    body: Element,
    request: RequestHeader,
    response: ResponseHeader,
    request_data: Optional[bytes],
) -> None:
    """A simple 'Hello, world!' application."""

    del head
    del request
    del response
    del request_data

    body.children.append(Element(tag="div", text="Hello, world!"))


# A default 'head' section to use in the HTML document.
HEAD = Element(
    tag="head",
    children=[
        Element(
            tag="meta",
            attrib=attributes({"charset": DEFAULT_ENCODING}),
        ),
        Element(
            tag="meta",
            attrib=attributes(
                {
                    "name": "viewport",
                    "content": "width=device-width, initial-scale=1",
                }
            ),
        ),
        Element(tag="title", text=HttpConnection.identity),
    ],
)


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

    # Create a copy at some point?
    head = HEAD

    body = Element(tag="body")

    # Create the application.
    await apps.get(request.target.path, default_app)(
        head, body, request, response, request_data
    )

    stream.write("<!DOCTYPE html>\n")
    html = Element(
        tag="html", attrib=attributes({"lang": "en"}), children=[head, body]
    )
    html.encode(stream)
