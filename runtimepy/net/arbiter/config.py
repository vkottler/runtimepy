"""
A module implementing a configuration-file interface for registering client
connections or servers.
"""

# built-in
from pathlib import Path as _Path
from site import addsitedir as _addsitedir
import socket as _socket
import sys
from typing import Any as _Any
from typing import Dict as _Dict
from typing import Iterable as _Iterable
from typing import List as _List
from typing import Optional as _Optional
from typing import cast as _cast

# third-party
from vcorelib.dict import merge as _merge
from vcorelib.dict.env import dict_resolve_env_vars, list_resolve_env_vars
from vcorelib.io import ARBITER as _ARBITER
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import find_file
from vcorelib.paths import normalize as _normalize

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

    directory: _Path

    def init(self, data: _JsonObject) -> None:
        """Perform implementation-specific initialization."""

        self.data = data

        port_overrides: _Dict[str, int] = data.get(
            "port_overrides",
            {},  # type: ignore
        )

        # Process ports.
        self.ports: _Dict[str, int] = {}
        for item in _cast(_List[_Dict[str, _Any]], data.get("ports", [])):
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

        self.app: _Optional[str] = data.get("app")  # type: ignore
        self.config: _Optional[_JsonObject] = _cast(
            _JsonObject, data.get("config")
        )

        self.factories: _List[_Any] = data.get("factories", [])  # type: ignore
        self.clients: _List[_Any] = data.get("clients", [])  # type: ignore
        self.servers: _List[_Any] = data.get("servers", [])  # type: ignore
        self.tasks: _List[_Any] = data.get("tasks", [])  # type: ignore
        self.structs: _List[_Any] = data.get("structs", [])  # type: ignore

        directory_str = str(data.get("directory", "."))
        self.directory = _Path(directory_str)

        # Add directory to Python path.
        if directory_str not in sys.path:
            sys.path.append(directory_str)

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

    async def load_configs(
        self, paths: _Iterable[_Pathlike], wait_for_stop: bool = False
    ) -> None:
        """Load a client and server configuration to the arbiter."""

        loaded = set()

        # Load and meld configuration data.
        config_data: _JsonObject = {}
        for path in paths:
            found = find_file(path, logger=self.logger, include_cwd=True)
            assert found is not None, f"Couldn't find '{path}'!"

            # Only load files once.
            absolute = found.resolve()
            if absolute not in loaded:
                _merge(
                    config_data,
                    _ARBITER.decode(
                        found,
                        includes_key="includes",
                        require_success=True,
                        logger=self.logger,
                    ).data,
                    logger=self.logger,
                )
                loaded.add(absolute)

        assert "root" not in self._config, self._config
        self._config["root"] = config_data  # type: ignore

        config = ConnectionArbiterConfig(data=config_data)

        # Set the directory to be the parent directory of the configuration
        # file if it wasn't set.
        if "directory" not in config.data:
            config.directory = _normalize(list(paths)[0]).parent

        # Add the site directory to facilitate module discovery.
        _addsitedir(str(config.directory))

        await self.process_config(config, wait_for_stop=wait_for_stop)

    async def process_config(
        self, config: ConnectionArbiterConfig, wait_for_stop: bool = False
    ) -> None:
        """Register clients and servers from a configuration object."""

        names = set()

        # Registier factories.
        for factory in config.factories:
            name = factory["name"]

            # Double specifying a factory (because of include shenanigans)
            # should be fine.
            if name not in names:
                assert self.register_module_factory(
                    name,
                    *factory.get("namespaces", []),
                    **dict_resolve_env_vars(
                        factory.get("kwargs", {}),
                        env=config.ports,  # type: ignore
                    ),
                ), f"Couldn't register factory '{factory}'!"
                names.add(name)

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

        # Register tasks.
        for task in config.tasks:
            name = task["name"]
            factory = task["factory"]
            assert self.factory_task(
                factory,
                name,
                period_s=task["period_s"],
                average_depth=task["average_depth"],
            ), f"Couldn't register task '{name}' ({factory})!"

        # Register structs.
        for struct in config.structs:
            name = struct["name"]
            factory = struct["factory"]
            assert self.factory_struct(
                struct["factory"], struct["name"], struct.get("config", {})
            ), f"Couldn't register struct '{name}' ({factory})!"

        # Set the new application entry if it's set.
        self.set_app(config.app, wait_for_stop=wait_for_stop)

        # Update application configuration data if necessary.
        if config.config is not None:
            root = self._config["root"]
            self._config = config.config
            assert "root" not in config.config, config.config
            config.config["root"] = root
