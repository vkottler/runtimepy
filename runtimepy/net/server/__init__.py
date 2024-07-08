"""
A module implementing a server interface for this package.
"""

# built-in
from io import StringIO
import logging
import mimetypes
from pathlib import Path
from typing import Any, Optional, TextIO

# third-party
from vcorelib.io import JsonObject
from vcorelib.paths import Pathlike, find_file, normalize

# internal
from runtimepy import DEFAULT_EXT, PKG_NAME
from runtimepy.channel.environment.command import GLOBAL
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.request_target import PathMaybeQuery
from runtimepy.net.http.response import ResponseHeader
from runtimepy.net.server.html import HtmlApp, HtmlApps, html_handler
from runtimepy.net.server.json import encode_json, json_handler
from runtimepy.net.tcp.http import HttpConnection

MIMETYPES_INIT = False


def package_data_dir() -> Path:
    """Get this package's data directory."""

    result = find_file(f"factories.{DEFAULT_EXT}", package=PKG_NAME)
    assert result is not None
    return result.parent


class RuntimepyServerConnection(HttpConnection):
    """A class implementing a server-connection interface for this package."""

    # Can register application methods to URL paths.
    apps: HtmlApps = {}
    default_app: Optional[HtmlApp] = None

    # Can load additional data into this dictionary for easy HTTP access.
    json_data: JsonObject = {"test": {"a": 1, "b": 2, "c": 3}}

    favicon_data: bytes

    paths: list[Path]
    class_paths: list[Pathlike] = [Path(), package_data_dir()]

    def add_path(self, path: Pathlike, front: bool = False) -> None:
        """Add a path."""

        resolved = normalize(path).resolve()
        if not front:
            self.paths.append(resolved)
        else:
            self.paths.insert(0, resolved)

        self.log_paths()

    def log_paths(self) -> None:
        """Log search paths."""

        self.logger.debug(
            "New path: %s.", ", ".join(str(x) for x in self.paths)
        )

    def init(self) -> None:
        """Initialize this instance."""

        global MIMETYPES_INIT  # pylint: disable=global-statement
        if not MIMETYPES_INIT:
            mimetypes.init()
            MIMETYPES_INIT = True

        super().init()

        # Initialize paths.
        self.paths = []
        for path in type(self).class_paths:
            self.add_path(path)

        # Load favicon if necessary.
        if not hasattr(type(self), "favicon_data"):
            with self.log_time("Loading favicon"):
                favicon = find_file("favicon.ico", package=PKG_NAME)
                assert favicon is not None
                with favicon.open("rb") as favicon_fd:
                    type(self).favicon_data = favicon_fd.read()

    def try_file(
        self, path: PathMaybeQuery, response: ResponseHeader
    ) -> Optional[bytes]:
        """Try serving this path as a file directly from the file-system."""

        result = None

        # Try serving the path as a file.
        for search in self.paths:
            candidate = search.joinpath(path[0][1:])
            if candidate.is_file():
                mime, encoding = mimetypes.guess_type(candidate, strict=False)

                # Set MIME type if it can be determined.
                if mime:
                    response["Content-Type"] = mime

                # We don't handle this yet.
                assert not encoding, (candidate, mime, encoding)

                self.logger.info("Serving '%s' (MIME: %s)", candidate, mime)

                # Return the file data.
                with candidate.open("rb") as path_fd:
                    result = path_fd.read()

                break

        return result

    def handle_command(
        self, stream: TextIO, response: ResponseHeader, args: tuple[str, ...]
    ) -> None:
        """Handle a command request."""

        response_data: dict[str, Any] = {"your_command": args}

        response_data["success"] = False
        response_data["message"] = "No command executed."

        if not args or args[0] not in GLOBAL:
            response_data["usage"] = (
                "/<environment (arg0)>/<arg1>[/.../<argN>]"
            )
            response_data["environments"] = list(GLOBAL)

        # Run command.
        else:
            result = GLOBAL[args[0]].command(" ".join(args[1:]))
            response_data["success"] = result.success
            response_data["message"] = str(result)

        # Send response.
        encode_json(stream, response, response_data)

    async def post_handler(
        self,
        response: ResponseHeader,
        request: RequestHeader,
        request_data: Optional[bytes],
    ) -> Optional[bytes]:
        """Handle POST requests."""

        request.log(self.logger, False, level=logging.INFO)

        result = None

        with StringIO() as stream:
            # Treat request as a command.
            if request.target.origin_form:
                self.handle_command(
                    stream, response, Path(request.target.path).parts[1:]
                )
                result = stream.getvalue().encode()

        return result

    async def get_handler(
        self,
        response: ResponseHeader,
        request: RequestHeader,
        request_data: Optional[bytes],
    ) -> Optional[bytes]:
        """Handle GET requests."""

        request.log(self.logger, False, level=logging.INFO)

        result = None

        with StringIO() as stream:
            if request.target.origin_form:
                path = request.target.path

                # Handle favicon (for browser clients).
                if path.startswith("/favicon"):
                    response["Content-Type"] = "image/x-icon"
                    return self.favicon_data

                # Try serving the path as a file.
                result = self.try_file(request.target.origin_form, response)
                if result is not None:
                    return result

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
