"""
A module implementing an application information interface.
"""

# built-in
import asyncio as _asyncio
from contextlib import AsyncExitStack as _AsyncExitStack
from dataclasses import dataclass
from logging import getLogger as _getLogger
from re import compile as _compile
from typing import Any, Dict
from typing import Iterator as _Iterator
from typing import MutableMapping as _MutableMapping
from typing import Type as _Type
from typing import TypeVar as _TypeVar

# third-party
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.logging import LoggerType as _LoggerType
from vcorelib.namespace import Namespace as _Namespace

# internal
from runtimepy.mapping import DEFAULT_PATTERN
from runtimepy.net.arbiter.result import OverallResult, results
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.manager import ConnectionManager
from runtimepy.struct import StructMap as _StructMap
from runtimepy.task import PeriodicTask, PeriodicTaskManager
from runtimepy.tui.mixin import TuiMixin

ConnectionMap = _MutableMapping[str, _Connection]
T = _TypeVar("T", bound=_Connection)
V = _TypeVar("V", bound=PeriodicTask)
Z = _TypeVar("Z")


@dataclass
class AppInfo:
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

    tasks: Dict[str, PeriodicTask]
    task_manager: PeriodicTaskManager[Any]

    # Keep track of application state.
    results: OverallResult

    # A name-to-struct mapping.
    structs: _StructMap

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
        )

    def search(
        self,
        *names: str,
        pattern: str = DEFAULT_PATTERN,
        kind: _Type[T] = _Connection,  # type: ignore
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

    def search_tasks(
        self, kind: _Type[V], pattern: str = ".*"
    ) -> _Iterator[V]:
        """Search for tasks by type or pattern."""

        compiled = _compile(pattern)

        for name, task in self.tasks.items():
            if compiled.search(name) is not None and isinstance(task, kind):
                yield task

    def single(
        self,
        *names: str,
        pattern: str = ".*",
        kind: _Type[T] = _Connection,  # type: ignore
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
