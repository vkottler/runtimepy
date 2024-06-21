"""
A module implementing an application information interface.
"""

# built-in
from abc import ABC as _ABC
import asyncio as _asyncio
from contextlib import AsyncExitStack as _AsyncExitStack
from dataclasses import dataclass
from logging import getLogger as _getLogger
from re import compile as _compile
from typing import Awaitable as _Awaitable
from typing import Callable as _Callable
from typing import Iterator as _Iterator
from typing import MutableMapping as _MutableMapping
from typing import TYPE_CHECKING, Any
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# third-party
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.logging import LoggerMixin as _LoggerMixin
from vcorelib.logging import LoggerType as _LoggerType
from vcorelib.namespace import Namespace as _Namespace

# internal
from runtimepy.channel.environment.sample import poll_sample_env, sample_env
from runtimepy.mapping import DEFAULT_PATTERN
from runtimepy.mixins.trig import TrigMixin
from runtimepy.net.arbiter.result import OverallResult, results
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.manager import ConnectionManager
from runtimepy.primitives import Uint32
from runtimepy.struct import RuntimeStructBase
from runtimepy.struct import StructMap as _StructMap
from runtimepy.task import PeriodicTask, PeriodicTaskManager
from runtimepy.tui.mixin import TuiMixin

if TYPE_CHECKING:
    from runtimepy.subprocess.peer import (
        RuntimepyPeer as _RuntimepyPeer,  # pragma: nocover
    )

ConnectionMap = _MutableMapping[str, _Connection]
T = _TypeVar("T", bound=_Connection)
V = _TypeVar("V", bound=PeriodicTask)
Z = _TypeVar("Z")


class RuntimeStruct(RuntimeStructBase, _ABC):
    """A class implementing a base runtime structure."""

    app: "AppInfo"

    def init_env(self) -> None:
        """Initialize this sample environment."""

    async def build(self, app: "AppInfo") -> None:
        """Build a struct instance's channel environment."""

        self.app = app
        self.init_env()


W = _TypeVar("W", bound=RuntimeStruct)


class TrigStruct(RuntimeStruct, TrigMixin):
    """A simple trig struct."""

    iterations: Uint32

    def init_env(self) -> None:
        """Initialize this sample environment."""

        TrigMixin.__init__(self, self.env)
        self.iterations = Uint32()
        self.env.int_channel("iterations", self.iterations, commandable=True)

    def poll(self) -> None:
        """
        A method that other runtime entities can call to perform canonical
        updates to this struct's environment.
        """

        # Pylint bug?
        self.dispatch_trig(self.iterations.value)  # pylint: disable=no-member
        self.iterations.value += 1  # pylint: disable=no-member


class SampleStruct(TrigStruct):
    """A sample runtime structure."""

    def init_env(self) -> None:
        """Initialize this sample environment."""

        sample_env(self.env)
        super().init_env()

    def poll(self) -> None:
        """
        A method that other runtime entities can call to perform canonical
        updates to this struct's environment.
        """
        super().poll()
        poll_sample_env(self.env)


@dataclass
class AppInfo(_LoggerMixin):
    """References provided to network applications."""

    # A logger for applications to use.
    logger: _LoggerType

    # An exit stack which can be used to ensure certain application resources
    # are cleaned up.
    stack: _AsyncExitStack

    # A connection map (names to instances).
    connections: ConnectionMap
    conn_manager: ConnectionManager

    # Connection names.
    names: _Namespace

    # A signal that, when set, indicates the application to begin shutting
    # down.
    stop: _asyncio.Event

    # Configuration data that may be specified in a configuration file.
    config: _JsonObject

    tui: TuiMixin

    tasks: dict[str, PeriodicTask]
    task_manager: PeriodicTaskManager[Any]

    # Keep track of application state.
    results: OverallResult

    # A name-to-struct mapping.
    structs: _StructMap

    # A name-to-peer mapping.
    peers: dict[str, "_RuntimepyPeer"]

    def with_new_logger(self, name: str) -> "AppInfo":
        """Get a copy of this AppInfo instance, but with a new logger."""

        return AppInfo(
            _getLogger(name),
            self.stack,
            self.connections,
            self.conn_manager,
            self.names,
            self.stop,
            self.config,
            self.tui,
            self.tasks,
            self.task_manager,
            self.results,
            self.structs,
            self.peers,
        )

    def search(
        self,
        *names: str,
        pattern: str = DEFAULT_PATTERN,
        kind: type[T] = _Connection,  # type: ignore
    ) -> _Iterator[T]:
        """
        Get all connections that are matching a naming convention or are
        specific kind (or both).
        """

        seen: set[T] = set()

        for name in self.names.search(*names, pattern=pattern):
            conn = self.connections[name]
            if isinstance(conn, kind):
                yield conn
                seen.add(conn)

        # Also check the connection manager (for server connections) if the
        # default pattern is used.
        if pattern == DEFAULT_PATTERN:
            for conn in self.conn_manager.by_type(kind):
                if conn not in seen:
                    yield conn
                    seen.add(conn)

    def search_tasks(self, kind: type[V], pattern: str = ".*") -> _Iterator[V]:
        """Search for tasks by type or pattern."""

        compiled = _compile(pattern)

        for name, task in self.tasks.items():
            if compiled.search(name) is not None and isinstance(task, kind):
                yield task

    def search_structs(
        self, kind: type[W], pattern: str = ".*"
    ) -> _Iterator[W]:
        """Search for structs by type or name."""

        compiled = _compile(pattern)

        for name, task in self.structs.items():
            if compiled.search(name) is not None and isinstance(task, kind):
                yield task

    def single(
        self,
        *names: str,
        pattern: str = ".*",
        kind: type[T] = _Connection,  # type: ignore
    ) -> T:
        """Search for a single node."""

        result = list(self.search(*names, pattern=pattern, kind=kind))
        assert len(result) == 1, result
        return result[0]

    async def all_finalized(self) -> None:
        """Wait for all tasks and connections to be finalized."""

        # Wait for all connections and tasks to be finalized.
        await _asyncio.gather(
            *(
                x.env.wait_finalized()
                for x in list(self.connections.values())
                + list(self.tasks.values())
            )
        )

    def exceptions(self) -> _Iterator[Exception]:
        """Iterate over exceptions raised by the application."""

        for stage in self.results:
            for result in stage:
                if result.exception is not None:
                    yield result.exception

    @property
    def raised_exception(self) -> bool:
        """Determine if the application raised any exception."""
        return bool(list(self.exceptions()))

    def result(self, logger: _LoggerType = None) -> bool:
        """Get the overall boolean result for the application."""

        if logger is not None and self.raised_exception:
            logger.error("An exception was not caught at runtime!")

        return results(self.results, logger=logger)

    def original_config(self) -> dict[str, Any]:
        """
        Re-assemble a dictionary closer to the original configuration data
        (than the .config attribute).
        """

        result: dict[str, Any] = {"config": {}}
        for key, val in self.config.items():
            if key != "root":
                result["config"][key] = val

        for key, val in self.config.get("root", {}).items():  # type: ignore
            if key != "config":
                result[key] = val

        return result

    def config_param(self, key: str, default: Z, strict: bool = False) -> Z:
        """Attempt to get a configuration parameter."""

        config: dict[str, Z] = self.config["root"].setdefault(  # type: ignore
            "config",
            {},
        )

        if strict:
            assert key in config, (key, config)

        return config.get(key, default)


NetworkApplication = _Callable[[AppInfo], _Awaitable[int]]
NetworkApplicationlike = _Union[NetworkApplication, list[NetworkApplication]]
ArbiterApps = list[list[NetworkApplication]]
