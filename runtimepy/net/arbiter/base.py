"""
A module implementing a base connection-arbiter interface.
"""

# built-in
import asyncio as _asyncio
from contextlib import AsyncExitStack as _AsyncExitStack
from contextlib import suppress as _suppress
from inspect import isawaitable as _isawaitable
from typing import Awaitable as _Awaitable
from typing import Iterable as _Iterable
from typing import MutableMapping as _MutableMapping
from typing import Optional
from typing import Union as _Union

# third-party
from vcorelib.asyncio import log_exceptions, run_handle_stop
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.logging import LoggerMixin as _LoggerMixin
from vcorelib.logging import LoggerType as _LoggerType
from vcorelib.math import TIMER
from vcorelib.namespace import Namespace as _Namespace
from vcorelib.namespace import NamespaceMixin as _NamespaceMixin

# internal
from runtimepy.channel.environment.command import (
    clear_env,
    env_json_data,
    register_env,
)
from runtimepy.net.arbiter.housekeeping import housekeeping
from runtimepy.net.arbiter.info import (
    AppInfo,
    ArbiterApps,
    ConnectionMap,
    NetworkApplication,
    NetworkApplicationlike,
    RuntimeStruct,
)
from runtimepy.net.arbiter.result import AppResult, ResultState
from runtimepy.net.arbiter.task import (
    ArbiterTaskManager as _ArbiterTaskManager,
)
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.manager import ConnectionManager as _ConnectionManager
from runtimepy.net.server import RuntimepyServerConnection
from runtimepy.subprocess.peer import RuntimepyPeer as _RuntimepyPeer
from runtimepy.tui.mixin import CursesWindow, TuiMixin

ServerTask = _Awaitable[None]
RuntimeProcessTask = tuple[type[_RuntimepyPeer], str, _JsonObject, str]


async def init_only(app: AppInfo) -> int:
    """A network application that doesn't do anything."""

    await app.all_finalized()
    return 0


def normalize_app(
    app: NetworkApplicationlike = None,
) -> ArbiterApps:
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
        metrics_poller_task: bool = True,
    ) -> None:
        """Initialize this connection arbiter."""

        _LoggerMixin.__init__(self, logger=logger)
        TuiMixin.__init__(self, window=window)

        if manager is None:
            manager = _ConnectionManager()
        self.manager = manager

        self.task_manager = _ArbiterTaskManager()

        # Ensure that connection metrics are polled.
        self.task_manager.register(
            housekeeping(
                self.manager, poll_connection_metrics=metrics_poller_task
            )
        )

        if stop_sig is None:
            stop_sig = _asyncio.Event()
        self.stop_sig = stop_sig

        _NamespaceMixin.__init__(self, namespace=namespace)

        # A fallback application. Set a class attribute so this can be more
        # easily externally updated.
        self._inits: ArbiterApps = []
        self._apps: ArbiterApps = normalize_app(app)

        # Application configuration data.
        if config is None:
            config = {}
        self._config = config

        # Keep track of connection objects.
        self._connections: ConnectionMap = {}
        self._deferred_connections: _MutableMapping[
            str, _Awaitable[_Connection]
        ] = {}

        # Runtime structures.
        self._structs: dict[str, RuntimeStruct] = {}

        # Runtime procesess.
        self._peers: dict[str, RuntimeProcessTask] = {}
        self._runtime_peers: dict[str, _RuntimepyPeer] = {}

        self._servers: list[_asyncio.Task[None]] = []
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

    def _setup_server_json(self, info: AppInfo) -> None:
        """Add runtime data to the server's JSON data structure."""

        cls = RuntimepyServerConnection

        # Connect configuration data.
        cls.json_data["config"] = info.original_config()

        # Connect environment data.
        cls.json_data["environments"] = env_json_data()

    def _register_envs(self) -> None:
        """Register environments."""

        for name, conn in self._connections.items():
            register_env(name, conn.command)
        for struct in self._structs.values():
            register_env(struct.name, struct.command)

    async def _init_connections(self) -> None:
        """Initialize network connections."""

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

    async def _build_structs(self, info: AppInfo) -> None:
        """Build structs."""

        with info.log_time("Building structs", reminder=True):
            await _asyncio.gather(
                *(x.build(info) for x in self._structs.values())
            )
            for struct in self._structs.values():
                struct.env.finalize(strict=False)

    async def _start_processes(self, stack: _AsyncExitStack) -> None:
        """Start processes."""

        for name, (peer, name, config, import_str) in self._peers.items():
            self._runtime_peers[name] = await stack.enter_async_context(
                peer.running_program(name, config, import_str)
            )
            self.logger.info("Started process '%s'.", name)

    async def _main(
        self,
        stack: _AsyncExitStack,
        app: NetworkApplicationlike = None,
        check_connections: bool = True,
        config: _JsonObject = None,
    ) -> tuple[int, Optional[AppInfo]]:
        """Main application entry."""

        result = -1
        info: Optional[AppInfo] = None

        clear_env()

        # Wait for servers to start.
        for _ in range(len(self._servers)):
            await self._servers_started.acquire()

        # Start processes.
        await self._start_processes(stack)

        with self.log_time("Connection initialization", reminder=True):
            await self._init_connections()

        # Register environments.
        self._register_envs()
        tasks = {x.name: x for x in self.task_manager.tasks}
        for task in tasks.values():
            register_env(task.name, task.command)

        # Run application, but only if all the registered connections
        # are still alive after initialization.
        if not check_connections or not any(
            x.disabled for x in self._connections.values()
        ):
            info = AppInfo(
                self.logger,
                stack,
                self._connections,
                self.manager,
                self._namespace,
                self.stop_sig,
                config if config is not None else self._config,
                self,
                tasks,  # type: ignore
                self.task_manager,
                [],
                self._structs,  # type: ignore
                self._runtime_peers,
            )

            # Build structs.
            await self._build_structs(info)

            # Initialize tasks.
            with info.log_time("Initializing periodic tasks", reminder=True):
                await _asyncio.gather(
                    *(x.init(info) for x in self.task_manager.tasks)
                )
                for task in self.task_manager.tasks:
                    task.env.finalize(strict=False)

            # Wire runtime data to server JSON.
            self._setup_server_json(info)

            # Start tasks.
            await stack.enter_async_context(
                self.task_manager.running(stop_sig=self.stop_sig)
            )

            # Run initialization methods.
            result = await self._run_apps_list(self._inits, info)
            if result == 0:
                # Get application methods.
                apps = self._apps
                if app is not None:
                    apps = normalize_app(app)

                # Run applications in order.
                result = await self._run_apps_list(apps, info)

        return result, info

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
        info: Optional[AppInfo] = None

        try:
            async with _AsyncExitStack() as stack:
                result, info = await self._main(
                    stack,
                    app=app,
                    check_connections=check_connections,
                    config=config,
                )
        finally:
            for conn in self._connections.values():
                conn.disable(f"app exit {result}")

            # Stop runtime entities.
            self.stop_sig.set()
            await _asyncio.sleep(0)

            # Summarize results.
            if info is not None:
                info.result(logger=self.logger)

        return result

    async def _run_apps_list(self, apps: ArbiterApps, info: AppInfo) -> int:
        """Run application methods."""

        # Run applications in order.
        result = 0
        for curr_app in apps:
            if result == 0:
                result = await self._run_apps(curr_app, info)

            # Populate "not run" statuses.
            else:
                info.results.append(
                    [AppResult(app.__name__) for app in curr_app]
                )

        return result

    async def _run_apps(
        self, apps: list[NetworkApplication], info: AppInfo
    ) -> int:
        """Run application methods in parallel."""

        pairs = [(app, info.with_new_logger(app.__name__)) for app in apps]

        # Pre-populate stage results with "not run" placeholders.
        stage_results = [AppResult(app.__name__) for app in apps]

        for _, inf in pairs:
            inf.logger.debug("Starting.")

        total = 0
        try:
            with TIMER.measure_ns() as token:
                results = await _asyncio.gather(
                    *(app(inf) for app, inf in pairs)
                )

            duration_ns = TIMER.result(token)

            for idx, result in enumerate(results):
                pairs[idx][1].logger.debug("Returned %d.", result)
                total += result

                # Capture a normal result.
                stage_results[idx] = AppResult(
                    apps[idx].__name__,
                    ResultState.from_int(result),
                    result,
                    duration_ns=duration_ns,
                )

        # Keep track of stages that raise an exception.
        except Exception as exc:  # pylint: disable=broad-exception-caught
            stage_results = [
                AppResult(app.__name__, ResultState.EXCEPTION, exception=exc)
                for app in apps
            ]
            total = -1

        # Keep track of this stage's results.
        info.results.append(stage_results)

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

        # Create task for connection manager.
        conns = _asyncio.create_task(self.manager.manage(self.stop_sig))

        # Run application.
        result = await self._entry(
            app=app, check_connections=check_connections, config=config
        )

        # Shutdown any pending tasks.
        pending = log_exceptions(self._servers + [conns], logger=self.logger)
        if pending:
            for task in pending:
                task.cancel()
                with _suppress(KeyboardInterrupt, _asyncio.CancelledError):
                    await task

            assert not log_exceptions(pending, logger=self.logger)

        return int(result)

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

        return run_handle_stop(
            self.stop_sig,
            self.app(
                app=app, check_connections=check_connections, config=config
            ),
            eloop=eloop,
            signals=signals,
            enable_uvloop=enable_uvloop,
        )
