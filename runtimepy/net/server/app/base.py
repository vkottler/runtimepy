"""
A module implementing a web application base.
"""

# built-in
from io import StringIO
import socket
from typing import Any, cast

# third-party
from svgen.element import Element
from vcorelib import DEFAULT_ENCODING
from vcorelib.io import IndentedFileWriter
from vcorelib.paths import find_file

# internal
from runtimepy import PKG_NAME
from runtimepy.net.arbiter.info import AppInfo


class WebApplication:
    """A simple web-application interface."""

    worker_source_paths = ["worker", "handle_json_messages"]
    main_source_paths = ["main"]

    def __init__(self, app: AppInfo) -> None:
        """Initialize this instance."""
        self.app = app

    def populate(self, body: Element) -> None:
        """Populate the body element with the application."""

        children = body.children
        children.append(Element(tag="div", text="Begin."))

        config: dict[str, Any] = self.app.config["root"]  # type: ignore

        # Find connection ports to save as variables in JavaScript.
        host = (
            socket.gethostname()
            if not config.get("config", {}).get("localhost", False)
            else "localhost"
        )

        for port in cast(list[dict[str, Any]], config["ports"]):
            if port["name"] == f"{PKG_NAME}_http_server":
                http_server = f"http://{host}:{port['port']}"
                children.append(
                    Element(tag="div", text=http_server, id="http_server_url")
                )
            elif port["name"] == f"{PKG_NAME}_websocket_server":
                websocket_server = f"ws://{host}:{port['port']}"
                children.append(
                    Element(
                        tag="div",
                        text=websocket_server,
                        id="websocket_server_url",
                    )
                )

        children.append(Element(tag="div", text="End."))

        # Worker code.
        with StringIO() as stream:
            writer = IndentedFileWriter(stream, per_indent=2)
            for path in self.worker_source_paths:
                self._write_found_file(
                    writer, f"package://{PKG_NAME}/{path}.js"
                )
            children.append(
                Element(
                    tag="script", type="text/js-worker", text=stream.getvalue()
                )
            )

        # Main-thread code.
        with StringIO() as stream:
            writer = IndentedFileWriter(stream, per_indent=2)
            for path in self.main_source_paths:
                self._write_found_file(
                    writer, f"package://{PKG_NAME}/{path}.js"
                )
            children.append(Element(tag="script", text=stream.getvalue()))

    def _write_found_file(
        self, writer: IndentedFileWriter, *args, **kwargs
    ) -> None:
        """Write a file's contents to the file-writer's stream."""

        entry = find_file(*args, **kwargs)
        assert entry is not None
        with entry.open(encoding=DEFAULT_ENCODING) as path_fd:
            for line in path_fd:
                writer.write(line)
