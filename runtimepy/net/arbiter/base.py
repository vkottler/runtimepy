"""
A module implementing a base connection-arbiter interface.
"""

# built-in
import asyncio as _asyncio
from contextlib import AsyncExitStack as _AsyncExitStack
from typing import Awaitable as _Awaitable
from typing import Callable as _Callable
from typing import Iterable as _Iterable
from typing import List as _List
from typing import MutableMapping as _MutableMapping

# third-party
from vcorelib.asyncio import run_handle_stop as _run_handle_stop
from vcorelib.logging import LoggerMixin as _LoggerMixin
from vcorelib.logging import LoggerType as _LoggerType
from vcorelib.namespace import Namespace as _Namespace
from vcorelib.namespace import NamespaceMixin as _NamespaceMixin

# internal
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.manager import ConnectionManager as _ConnectionManager

ConnectionMap = _MutableMapping[str, _Connection]
NetworkApplication = _Callable[
    [_AsyncExitStack, ConnectionMap], _Awaitable[int]
]
ServerTask = _Awaitable[None]


async def init_only(stack: _AsyncExitStack, connections: ConnectionMap) -> int:
    """A network application that doesn't do anything."""

    del stack
    del connections
    return 0


class BaseConnectionArbiter(_NamespaceMixin, _LoggerMixin):
    """
    A class implementing a base connection-manager for a broader application.
    """

    def __init__(
        self,
        manager: _ConnectionManager = None,
        stop_sig: _asyncio.Event = None,
        namespace: _Namespace = None,
        logger: _LoggerType = None,
    ) -> None:
        """Initialize this connection arbiter."""

        _LoggerMixin.__init__(self, logger=logger)

        if manager is None:
            manager = _ConnectionManager()
        self.manager = manager

        if stop_sig is None:
            stop_sig = _asyncio.Event()
        self.stop_sig = stop_sig

        _NamespaceMixin.__init__(self, namespace=namespace)

        # Keep track of connection objects.
        self._connections: ConnectionMap = {}
        self._servers: _List[ServerTask] = []

        self._init()

    def _init(self) -> None:
        """Additional initialization tasks."""

    def register_connection(
        self,
        connection: _Connection,
        *names: str,
        delim: str = None,
    ) -> bool:
        """Attempt to register a connection object."""

        result = False

        with self.names_pushed(*names):
            name = self.namespace(delim=delim)

        if name not in self._connections:
            self._connections[name] = connection
            self.manager.queue.put_nowait(connection)
            result = True
            connection.logger.info("Registered as '%s'.", name)

        return result

    async def _entry(
        self, app: NetworkApplication, check_connections: bool = True
    ) -> int:
        """
        Ensures connections are given a chance to initialize, run the
        application, clean up connections and return the application's result.
        """

        result = -1

        try:
            # Ensure connections are all initialized.
            await _asyncio.gather(
                *(x.initialized.wait() for x in self._connections.values())
            )

            self.logger.info("Connections initialized.")

            # Run application, but only if all the registered connections are
            # still alive after initialization.
            if not check_connections or not any(
                x.disabled for x in self._connections.values()
            ):
                async with _AsyncExitStack() as stack:
                    self.logger.info("Application starting.")
                    result = await app(stack, self._connections)
                    self.logger.info("Application returned %d.", result)

        finally:
            for conn in self._connections.values():
                conn.disable(f"app exit {result}")
            self.stop_sig.set()

        return result

    async def app(
        self,
        app: NetworkApplication = init_only,
        check_connections: bool = True,
    ) -> int:
        """
        Run the application alongside the connection manager and server tasks.
        """

        result = await _asyncio.gather(
            self._entry(app, check_connections=check_connections),
            self.manager.manage(self.stop_sig),
            *self._servers,
        )
        return int(result[0])

    def run(
        self,
        app: NetworkApplication = init_only,
        eloop: _asyncio.AbstractEventLoop = None,
        signals: _Iterable[int] = None,
        check_connections: bool = True,
    ) -> int:
        """Run the application until the stop signal is set."""

        return _run_handle_stop(
            self.stop_sig,
            self.app(app=app, check_connections=check_connections),
            eloop=eloop,
            signals=signals,
        )
