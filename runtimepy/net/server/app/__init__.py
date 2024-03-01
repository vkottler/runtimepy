"""
A module implementing application methods for this package's server interface.
"""

# built-in
from typing import Any, Optional

# third-party
from svgen.element.html import Html

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader
from runtimepy.net.server import RuntimepyServerConnection
from runtimepy.net.server.app.base import WebApplication

DOCUMENT = None


async def setup(app: AppInfo) -> int:
    """Perform server application setup steps."""

    async def main(
        document: Html,
        request: RequestHeader,
        response: ResponseHeader,
        request_data: Optional[bytes],
    ) -> Html:
        """A simple 'Hello, world!' application."""

        # Use the already-rendered document.
        config: dict[str, Any] = app.config["root"]  # type: ignore
        if config.get("config", {}).get("caching", True):
            global DOCUMENT  # pylint: disable=global-statement
            if DOCUMENT is not None:
                return DOCUMENT

        # Not currently used.
        del request
        del response
        del request_data

        # Create the application.
        WebApplication(app).populate(document.body)

        DOCUMENT = document
        return document

    RuntimepyServerConnection.default_app = main

    return 0
