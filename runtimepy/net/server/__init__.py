"""
A module implementing a server interface for this package.
"""

# built-in
from io import StringIO
from typing import Optional

# third-party
from vcorelib.io import JsonObject
from vcorelib.paths import find_file

# internal
from runtimepy import PKG_NAME
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader
from runtimepy.net.server.html import HtmlApp, HtmlApps, html_handler
from runtimepy.net.server.json import json_handler
from runtimepy.net.tcp.http import HttpConnection


class RuntimepyServerConnection(HttpConnection):
    """A class implementing a server-connection interface for this package."""

    # Can register application methods to URL paths.
    apps: HtmlApps = {}
    default_app: Optional[HtmlApp] = None

    # Can load additional data into this dictionary for easy HTTP access.
    json_data: JsonObject = {"test": {"a": 1, "b": 2, "c": 3}}

    favicon_data: bytes

    def init(self) -> None:
        """Initialize this instance."""

        super().init()

        # Load favicon if necessary.
        if not hasattr(type(self), "favicon_data"):
            with self.log_time("Loading favicon"):
                favicon = find_file("favicon.ico", package=PKG_NAME)
                assert favicon is not None
                with favicon.open("rb") as favicon_fd:
                    type(self).favicon_data = favicon_fd.read()

    async def get_handler(
        self,
        response: ResponseHeader,
        request: RequestHeader,
        request_data: Optional[bytes],
    ) -> Optional[bytes]:
        """Sample handler."""

        result = None

        with StringIO() as stream:
            if request.target.origin_form:
                path = request.target.path

                # Handle favicon (for browser clients).
                if path.startswith("/favicon"):
                    response["Content-Type"] = "image/x-icon"
                    return self.favicon_data

                # Handle raw data queries.
                if path.startswith("/json"):
                    json_handler(
                        stream,
                        request,
                        response,
                        request_data,
                        self.json_data,
                    )

                # Serve the application.
                else:
                    await html_handler(
                        type(self).apps,
                        stream,
                        request,
                        response,
                        request_data,
                        default_app=type(self).default_app,
                    )

                result = stream.getvalue().encode()

        return result
