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

    worker_source_paths = ["JsonConnection", "DataConnection", "worker"]
    main_source_paths = ["main", "config"]

    def __init__(self, app: AppInfo) -> None:
        """Initialize this instance."""
        self.app = app

    def _populate_server_urls(self, body: Element) -> None:
        """
        Add elements to the document that allow easy lookup from JavaScript.
        """

        children = body.children

        config: dict[str, Any] = self.app.config["root"]  # type: ignore

        # Find connection ports to save as variables in JavaScript.
        host = (
            socket.gethostname()
            if not config.get("config", {}).get("localhost", False)
            else "localhost"
        )

        for port in cast(list[dict[str, Any]], config["ports"]):
            text = ""
            ident = ""

            if port["name"] == f"{PKG_NAME}_http_server":
                text = f"http://{host}:{port['port']}"
                ident = "http_url"
            elif port["name"] == f"{PKG_NAME}_websocket_json_server":
                text = f"ws://{host}:{port['port']}"
                ident = "websocket_json_url"
            elif port["name"] == f"{PKG_NAME}_websocket_data_server":
                text = f"ws://{host}:{port['port']}"
                ident = "websocket_data_url"

            # Add element.
            if text and ident:
                children.append(Element(tag="div", text=text, id=ident))

    def populate(self, body: Element) -> None:
        """Populate the body element with the application."""

        children = body.children

        children.append(Element(tag="div", text="Begin."))
        self._populate_server_urls(body)
        children.append(Element(tag="div", text="End."))

        # Worker code.
        with StringIO() as stream:
            writer = IndentedFileWriter(stream, per_indent=2)
            for path in self.worker_source_paths:
                self._write_found_file(
                    writer, f"package://{PKG_NAME}/js/{path}.js"
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
                    writer, f"package://{PKG_NAME}/js/{path}.js"
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
