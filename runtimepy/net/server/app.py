"""
A module implementing application methods for this package's server interface.
"""

# built-in
from typing import Any, Optional, cast

# third-party
from svgen.element import Element
from svgen.element.html import Html

# internal
from runtimepy import PKG_NAME
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader
from runtimepy.net.server import RuntimepyServerConnection
from runtimepy.net.server.html import HtmlApp

DOCUMENT = None


def create_app(app: AppInfo) -> HtmlApp:
    """Create the main web application."""

    async def main(
        document: Html,
        request: RequestHeader,
        response: ResponseHeader,
        request_data: Optional[bytes],
    ) -> Html:
        """A simple 'Hello, world!' application."""

        # Use the already-rendered document.
        global DOCUMENT  # pylint: disable=global-statement
        if DOCUMENT is not None:
            return DOCUMENT

        del request
        del response
        del request_data

        config: dict[str, Any] = app.config["root"]  # type: ignore

        # Need to figure out writing interface for this + handling indent.
        # Should we just solve it by default on the svgen side?
        script_text = "console.log('wuddup');\nconsole.log('wuddup');"

        # Find connection ports to save as variables in JavaScript.
        for port in cast(list[dict[str, Any]], config["ports"]):
            if port["name"] == f"{PKG_NAME}_http_server":
                print(port)
            elif port["name"] == f"{PKG_NAME}_websocket_server":
                print(port)

        body = document.body.children
        body.append(Element(tag="div", text="Main application."))
        body.append(Element(tag="script", text=script_text))

        DOCUMENT = document
        return document

    return main


async def setup(app: AppInfo) -> int:
    """Perform server application setup steps."""
    RuntimepyServerConnection.default_app = create_app(app)
    return 0
