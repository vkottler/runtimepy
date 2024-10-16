"""
A module implementing a configuration-file interface for registering client
connections or servers.
"""

# built-in
from importlib import import_module as _import_module
from site import addsitedir as _addsitedir
import sys
from typing import Any as _Any
from typing import Callable as _Callable
from typing import Iterable as _Iterable

# third-party
from vcorelib.dict import merge as _merge
from vcorelib.dict.env import dict_resolve_env_vars, list_resolve_env_vars
from vcorelib.io import ARBITER as _ARBITER
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.logging import LoggerMixin as _LoggerMixin
from vcorelib.names import import_str_and_item
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import find_file
from vcorelib.paths import normalize as _normalize

# internal
from runtimepy import DEFAULT_EXT, PKG_NAME
from runtimepy.net.arbiter.config.codec import ConnectionArbiterConfig
from runtimepy.net.arbiter.config.util import fix_args, fix_kwargs, list_adder
from runtimepy.net.arbiter.imports import (
    ImportConnectionArbiter as _ImportConnectionArbiter,
)
from runtimepy.net.arbiter.imports.util import get_apps

ConfigObject = dict[str, _Any]
ConfigBuilder = _Callable[[ConfigObject], None]


def handle_config_builders(data: ConfigObject, logger: _LoggerMixin) -> None:
    """Run any configured configuration-data building methods."""

    for builder in data.get("config_builders", []):
        module, method = import_str_and_item(str(builder))
        with logger.log_time("Running config-builder '%s'", builder):
            getattr(_import_module(module), method)(data)


class ConfigConnectionArbiter(_ImportConnectionArbiter):
    """
    A class implementing a configuration loading interface for the connection
    arbiter.
    """

    search_packages: list[str] = []

    @classmethod
    def add_search_package(cls, name: str, front: bool = True) -> None:
        """Add a package to the search path."""

        name = name.replace("-", "_")
        if name not in cls.search_packages:
            list_adder(cls.search_packages, name, front=front)

    async def load_configs(
        self, paths: _Iterable[_Pathlike], wait_for_stop: bool = False
    ) -> None:
        """Load a client and server configuration to the arbiter."""

        loaded = set()

        # Load and meld configuration data.
        config_data: _JsonObject = {}
        for path in paths:
            # Try the path itself.
            found = find_file(path, logger=self.logger, include_cwd=True)

            # Try package search path next.
            if found is None:
                for pkg in self.search_packages:
                    found = find_file(
                        f"{path}.{DEFAULT_EXT}",
                        logger=self.logger,
                        package=pkg,
                    )
                    if found is not None:
                        break

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

        # Add the working directory and parent directories for module loading
        # / package discovery.
        directories = set(str(_normalize(x).parent) for x in paths)

        directories.add(
            str(
                config_data.setdefault(
                    "directory", str(_normalize(".").resolve())
                )
            )
        )

        for directory in directories:
            # Add the site directory to facilitate module discovery.
            _addsitedir(directory)

            # Add directory to Python path.
            if directory not in sys.path:
                sys.path.append(directory)

        # Run any JIT config methods.
        handle_config_builders(config_data, self)

        assert "root" not in self._config, self._config
        self._config["root"] = config_data  # type: ignore

        await self.process_config(
            ConnectionArbiterConfig(data=config_data),
            wait_for_stop=wait_for_stop,
        )

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
            kwargs.setdefault("markdown", client.get("markdown"))

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
                markdown=task.get("markdown"),
            ), f"Couldn't register task '{name}' ({factory})!"

        # Register structs.
        for struct in config.structs:
            name = struct["name"]
            factory = struct["factory"]
            assert self.factory_struct(
                struct["factory"], struct["name"], struct.get("config", {})
            ), f"Couldn't register struct '{name}' ({factory})!"

        # Register processes.
        for process in config.processes:
            name = process["name"]
            factory = process["factory"]
            assert self.factory_process(
                factory,
                name,
                process,
            ), f"Couldn't register process '{name}' ({factory})!"

        # Load initialization methods.
        self._inits = get_apps(config.inits)

        # Set the new application entry if it's set.
        apps = get_apps(config.app, wait_for_stop=wait_for_stop)
        if apps:
            self._apps = apps

        # Update application configuration data if necessary.
        if config.config is not None:
            root = self._config["root"]
            self._config = config.config
            assert "root" not in config.config, config.config
            config.config["root"] = root


ConfigConnectionArbiter.add_search_package(PKG_NAME)
