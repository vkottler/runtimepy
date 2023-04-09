"""
A module implementing a configuration-file interface for registering client
connections or servers.
"""

# built-in
import socket as _socket
from typing import Any as _Any
from typing import Dict as _Dict
from typing import List as _List
from typing import cast as _cast

# third-party
from vcorelib.dict.env import dict_resolve_env_vars, list_resolve_env_vars
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.paths import Pathlike as _Pathlike

# internal
from runtimepy.net import get_free_socket_name, normalize_host
from runtimepy.net.arbiter.imports import (
    ImportConnectionArbiter as _ImportConnectionArbiter,
)
from runtimepy.schemas import RuntimepyDictCodec as _RuntimepyDictCodec


class ConnectionArbiterConfig(_RuntimepyDictCodec):
    """
    A class for encoding and decoding connection-arbiter configuration data.
    """

    def init(self, data: _JsonObject) -> None:
        """Perform implementation-specific initialization."""

        self.data = data

        # Process ports.
        self.ports: _Dict[str, int] = {}
        for item in _cast(_List[_Dict[str, _Any]], data.get("ports", [])):
            self.ports[item["name"]] = get_free_socket_name(
                local=normalize_host(item["host"], item["port"]),
                kind=_socket.SOCK_STREAM
                if item["type"] == "tcp"
                else _socket.SOCK_DGRAM,
            ).port

        self.app: str = data["app"]  # type: ignore
        self.factories: _List[_Any] = data.get("factories", [])  # type: ignore
        self.clients: _List[_Any] = data.get("clients", [])  # type: ignore
        self.servers: _List[_Any] = data.get("servers", [])  # type: ignore

    def asdict(self) -> _JsonObject:
        """Obtain a dictionary representing this instance."""
        return self.data


def fix_kwargs(data: _Dict[str, _Any]) -> _Dict[str, _Any]:
    """
    Fix data depending on nuances of what some Python interfaces require.
    """

    # Convert some keys to tuples.
    for key in ["local_addr", "remote_addr"]:
        if key in data:
            data[key] = tuple(data[key])

    return data


def fix_args(data: _List[_Any], ports: _Dict[str, int]) -> _List[_Any]:
    """Fix positional arguments."""

    for idx, item in enumerate(data):
        # Allow port variables to be used in host strings.
        if isinstance(item, str):
            data[idx] = ":".join(
                str(x)
                for x in list_resolve_env_vars(
                    item.split(":"),
                    env=ports,  # type: ignore
                )
            )

    return data


class ConfigConnectionArbiter(_ImportConnectionArbiter):
    """
    A class implementing a configuration loading interface for the connection
    arbiter.
    """

    async def load_config(self, path: _Pathlike) -> None:
        """Load a client and server configuration to the arbiter."""
        await self.process_config(ConnectionArbiterConfig.decode(path))

    async def process_config(self, config: ConnectionArbiterConfig) -> None:
        """Register clients and servers from a configuration object."""

        # Registier factories.
        for factory in config.factories:
            name = factory["name"]
            assert self.register_module_factory(
                name,
                *factory.get("namespaces", []),
                **factory.get("kwargs", {}),
            ), "Couldn't register factory '{name}'!"

        # Register clients.
        for client in config.clients:
            factory = client["factory"]
            name = client["name"]

            # Resolve any port variables that may have been used.
            args = list_resolve_env_vars(
                client.get("args", []), env=config.ports  # type: ignore
            )
            kwargs = dict_resolve_env_vars(
                client.get("kwargs", {}), env=config.ports  # type: ignore
            )

            assert await self.factory_client(
                factory,
                name,
                *fix_args(args, config.ports),
                defer=client["defer"],
                # Perform some known fixes for common keyword arguments.
                **fix_kwargs(kwargs),
            ), f"Couldn't register client '{name}' ({factory})!"

        # Register servers.
        for server in config.servers:
            factory = server["factory"]

            assert await self.factory_server(
                factory,
                *list_resolve_env_vars(
                    server.get("args", []), env=config.ports  # type: ignore
                ),
                **dict_resolve_env_vars(
                    server.get("kwargs", {}), env=config.ports  # type: ignore
                ),
            ), f"Couldn't register a '{factory}' server!"

        # Set the new (default) application entry.
        self.set_app(config.app)
