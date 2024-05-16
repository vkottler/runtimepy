"""
A module implementing the configuration-object codec interface.
"""

# built-in
from pathlib import Path as _Path
import socket as _socket
from typing import Any as _Any
from typing import Optional as _Optional
from typing import Union as _Union
from typing import cast as _cast

# third-party
from vcorelib.io.types import JsonObject as _JsonObject

# internal
from runtimepy.net import get_free_socket_name, normalize_host
from runtimepy.schemas import RuntimepyDictCodec as _RuntimepyDictCodec

ConfigApps = _Optional[_Union[str, list[str]]]


class ConnectionArbiterConfig(_RuntimepyDictCodec):
    """
    A class for encoding and decoding connection-arbiter configuration data.
    """

    directory: _Path

    def init(self, data: _JsonObject) -> None:
        """Perform implementation-specific initialization."""

        self.data = data

        port_overrides: dict[str, int] = data.get(
            "port_overrides",
            {},  # type: ignore
        )

        # Process ports.
        self.ports: dict[str, int] = {}
        for item in _cast(list[dict[str, _Any]], data.get("ports", [])):
            port = get_free_socket_name(
                local=normalize_host(
                    item["host"],
                    port_overrides.get(item["name"], item["port"]),
                ),
                kind=(
                    _socket.SOCK_STREAM
                    if item["type"] == "tcp"
                    else _socket.SOCK_DGRAM
                ),
            ).port

            # Update the original structure.
            self.ports[item["name"]] = port
            item["port"] = port

        self.app: ConfigApps = data.get("app")  # type: ignore
        self.inits: ConfigApps = data.get("init")  # type: ignore
        self.config: _Optional[_JsonObject] = _cast(
            _JsonObject, data.get("config")
        )

        self.factories: list[_Any] = data.get("factories", [])  # type: ignore
        self.clients: list[_Any] = data.get("clients", [])  # type: ignore
        self.servers: list[_Any] = data.get("servers", [])  # type: ignore
        self.tasks: list[_Any] = data.get("tasks", [])  # type: ignore
        self.structs: list[_Any] = data.get("structs", [])  # type: ignore
        self.processes: list[_Any] = data.get("processes", [])  # type: ignore

        self.directory = _Path(str(data.get("directory", ".")))

    def asdict(self) -> _JsonObject:
        """Obtain a dictionary representing this instance."""
        return self.data
