"""
A module implementing an interface extension to the base connection-arbiter so
that methods that create connections can be registered by name.
"""

# built-in
import asyncio as _asyncio

# third-party
from vcorelib.names import obj_class_to_snake

# internal
from runtimepy.net.arbiter.base import (
    BaseConnectionArbiter as _BaseConnectionArbiter,
)
from runtimepy.net.arbiter.base import ServerTask as _ServerTask
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.manager import ConnectionManager as _ConnectionManager


class ConnectionFactory:
    """An interface for creating client connections."""

    async def client(self, name: str, *args, **kwargs) -> _Connection:
        """Create a client connection."""
        raise NotImplementedError

    async def server_task(
        self,
        stop_sig: _asyncio.Event,
        manager: _ConnectionManager,
        started_sem: _asyncio.Semaphore,
        *args,
        **kwargs,
    ) -> _ServerTask:
        """Create a task that will run a connection server."""
        raise NotImplementedError


class FactoryConnectionArbiter(_BaseConnectionArbiter):
    """
    A class implementing an interface to allow connection factories to be
    used for creating new connections (that can then be registered).
    """

    def _init(self) -> None:
        """Additional initialization tasks."""

        super()._init()
        self._conn_factories: dict[str, ConnectionFactory] = {}
        self._conn_names: dict[ConnectionFactory, list[str]] = {}

    def register_connection_factory(
        self, factory: ConnectionFactory, *namespaces: str
    ) -> bool:
        """Attempt to register a connection factory."""

        result = False

        assert isinstance(factory, ConnectionFactory), factory

        name = factory.__class__.__name__
        snake_name = obj_class_to_snake(factory)

        if (
            name not in self._conn_factories
            and snake_name not in self._conn_factories
        ):
            self._conn_factories[name] = factory
            self._conn_factories[snake_name] = factory
            self._conn_names[factory] = [*namespaces]

            result = True
            self.logger.debug(
                "Registered '%s' (%s) connection factory.", name, snake_name
            )

        return result

    async def factory_client(
        self, factory: str, name: str, *args, defer: bool = False, **kwargs
    ) -> bool:
        """
        Attempt to register a client connection using a registered factory.
        """

        result = False

        if factory in self._conn_factories:
            factory_inst = self._conn_factories[factory]

            conn = factory_inst.client(name, *args, **kwargs)
            if not defer:
                conn = await conn  # type: ignore

            result = self.register_connection(
                conn, *self._conn_names[factory_inst], name
            )

        return result

    async def factory_server(self, factory: str, *args, **kwargs) -> bool:
        """Attempt to create a server task using a registered factory."""

        result = False

        if factory in self._conn_factories:
            factory_inst = self._conn_factories[factory]
            self._servers.append(
                _asyncio.create_task(
                    await factory_inst.server_task(  # type: ignore
                        self.stop_sig,
                        self.manager,
                        self._servers_started,
                        *args,
                        **kwargs,
                    )
                )
            )
            result = True

        return result
