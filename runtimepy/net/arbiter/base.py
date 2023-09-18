"""
A module implementing a base connection-arbiter interface.
"""

# built-in
import asyncio as _asyncio
from contextlib import AsyncExitStack as _AsyncExitStack
from inspect import isawaitable as _isawaitable
from typing import Awaitable as _Awaitable
from typing import Callable as _Callable
from typing import Iterable as _Iterable
from typing import List as _List
from typing import MutableMapping as _MutableMapping
from typing import Optional
from typing import Union as _Union

# third-party
from vcorelib.asyncio import run_handle_stop as _run_handle_stop
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.logging import LoggerMixin as _LoggerMixin
from vcorelib.logging import LoggerType as _LoggerType
from vcorelib.namespace import Namespace as _Namespace
from vcorelib.namespace import NamespaceMixin as _NamespaceMixin

# internal
from runtimepy.net.arbiter.housekeeping import metrics_poller
from runtimepy.net.arbiter.info import AppInfo, ConnectionMap
from runtimepy.net.arbiter.task import (
    ArbiterTaskManager as _ArbiterTaskManager,
)
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.manager import ConnectionManager as _ConnectionManager
from runtimepy.tui.mixin import CursesWindow, TuiMixin

NetworkApplication = _Callable[[AppInfo], _Awaitable[int]]
NetworkApplicationlike = _Union[NetworkApplication, _List[NetworkApplication]]
ServerTask = _Awaitable[None]


async def init_only(app: AppInfo) -> int:
    """A network application that doesn't do anything."""

    del app
    return 0


def normalize_app(
    app: NetworkApplicationlike = None,
) -> _List[_List[NetworkApplication]]:
    """
    Normalize some application parameter into a list of network applications.
    """

    if app is None:
        app = [init_only]

    if not isinstance(app, list):
        app = [app]

    return [app]


class BaseConnectionArbiter(_NamespaceMixin, _LoggerMixin, TuiMixin):
    """
    A class implementing a base connection-manager for a broader application.
    """

    def __init__(
        self,
        manager: _ConnectionManager = None,
        stop_sig: _asyncio.Event = None,
        namespace: _Namespace = None,
        logger: _LoggerType = None,
        app: NetworkApplicationlike = None,
        config: _JsonObject = None,
        window: Optional[CursesWindow] = None,
    ) -> None:
        """Initialize this connection arbiter."""

        _LoggerMixin.__init__(self, logger=logger)
        TuiMixin.__init__(self, window=window)

        if manager is None:
            manager = _ConnectionManager()
        self.manager = manager

        self.task_manager = _ArbiterTaskManager()

        # Ensure that connection metrics are polled.
        self.task_manager.register(metrics_poller(self.manager))

        if stop_sig is None:
            stop_sig = _asyncio.Event()
        self.stop_sig = stop_sig

        _NamespaceMixin.__init__(self, namespace=namespace)

        # A fallback application. Set a class attribute so this can be more
        # easily externally updated.
        self._apps: _List[_List[NetworkApplication]] = normalize_app(app)

        # Application configuration data.
        if config is None:
            config = {}
        self._config = config

        # Keep track of connection objects.
        self._connections: ConnectionMap = {}
        self._deferred_connections: _MutableMapping[
            str, _Awaitable[_Connection]
        ] = {}

        self._servers: _List[_asyncio.Task[None]] = []
        self._servers_started = _asyncio.Semaphore(0)

        self._init()

    def _init(self) -> None:
        """Additional initialization tasks."""

    def _register_connection(self, connection: _Connection, name: str) -> None:
        """Perform connection registration."""

        self._connections[name] = connection
        self.manager.queue.put_nowait(connection)
        connection.logger.info("Registered as '%s'.", name)

    def register_connection(
        self,
        connection: _Union[_Connection, _Awaitable[_Connection]],
        *names: str,
        delim: str = None,
    ) -> bool:
        """Attempt to register a connection object."""

        result = False

        with self.names_pushed(*names):
            name = self.namespace(delim=delim)

        if (
            name not in self._connections
            and name not in self._deferred_connections
        ):
            if _isawaitable(connection):
                self._deferred_connections[name] = connection
            else:
                assert isinstance(connection, _Connection)
                self._register_connection(connection, name)

            result = True

        return result

    async def _entry(
        self,
        app: NetworkApplicationlike = None,
        check_connections: bool = True,
        config: _JsonObject = None,
    ) -> int:
        """
        Ensures connections are given a chance to initialize, run the
        application, clean up connections and return the application's result.
        """

        result = -1

        try:
            # Wait for servers to start.
            for _ in range(len(self._servers)):
                await self._servers_started.acquire()

            # Start deferred connections.
            for key, value in zip(
                self._deferred_connections,
                await _asyncio.gather(*self._deferred_connections.values()),
            ):
                self._register_connection(value, key)

            # Ensure connections are all initialized.
            await _asyncio.gather(
                *(x.initialized.wait() for x in self._connections.values())
            )

            self.logger.info("Connections initialized.")

            tasks = {x.name: x for x in self.task_manager.tasks}

            # Run application, but only if all the registered connections are
            # still alive after initialization.
            if not check_connections or not any(
                x.disabled for x in self._connections.values()
            ):
                async with _AsyncExitStack() as stack:
                    self.logger.info("Application starting.")

                    info = AppInfo(
                        self.logger,
                        stack,
                        self._connections,
                        self._namespace,
                        self.stop_sig,
                        config if config is not None else self._config,
                        self,
                        tasks,  # type: ignore
                    )

                    # Initialize tasks.
                    self.logger.debug("Initializing periodic tasks...")
                    await _asyncio.gather(
                        *(x.init(info) for x in self.task_manager.tasks)
                    )
                    for task in self.task_manager.tasks:
                        task.env.finalize(strict=False)
                    self.logger.debug("Periodic tasks initialized.")

                    # Start tasks.
                    self.logger.debug("Starting periodic tasks...")
                    await stack.enter_async_context(
                        self.task_manager.running(stop_sig=self.stop_sig)
                    )
                    self.logger.debug("Periodic tasks started.")

                    # Get application methods.
                    apps = self._apps
                    if app is not None:
                        apps = normalize_app(app)

                    # Run applications in order.
                    result = 0
                    for curr_app in apps:
                        if result == 0:
                            result = await self._run_apps(curr_app, info)

        finally:
            for conn in self._connections.values():
                conn.disable(f"app exit {result}")
            self.stop_sig.set()

        return result

    async def _run_apps(
        self, apps: _List[NetworkApplication], info: AppInfo
    ) -> int:
        """Run application methods in parallel."""

        pairs = [(app, info.with_new_logger(app.__name__)) for app in apps]

        for _, inf in pairs:
            inf.logger.info("Starting.")

        total = 0
        try:
            results = await _asyncio.gather(*(app(inf) for app, inf in pairs))
            for idx, result in enumerate(results):
                pairs[idx][1].logger.info("Returned %d.", result)
                total += result

        except AssertionError as exc:
            info.logger.exception("Failed an assertion:", exc_info=exc)
            total = -1

        return total

    async def app(
        self,
        app: NetworkApplicationlike = None,
        check_connections: bool = True,
        config: _JsonObject = None,
    ) -> int:
        """
        Run the application alongside the connection manager and server tasks.
        """

        result = await _asyncio.gather(
            self._entry(
                app=app, check_connections=check_connections, config=config
            ),
            self.manager.manage(self.stop_sig),
            *self._servers,
        )
        return int(result[0])

    def run(
        self,
        app: NetworkApplicationlike = None,
        eloop: _asyncio.AbstractEventLoop = None,
        signals: _Iterable[int] = None,
        check_connections: bool = True,
        config: _JsonObject = None,
        enable_uvloop: bool = True,
    ) -> int:
        """Run the application until the stop signal is set."""

        return _run_handle_stop(
            self.stop_sig,
            self.app(
                app=app, check_connections=check_connections, config=config
            ),
            eloop=eloop,
            signals=signals,
            enable_uvloop=enable_uvloop,
        )
