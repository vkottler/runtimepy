"""
A module implementing an application information interface.
"""

# built-in
import asyncio as _asyncio
from contextlib import AsyncExitStack as _AsyncExitStack
from dataclasses import dataclass
from logging import getLogger as _getLogger
from re import compile as _compile
from typing import Dict
from typing import Iterator as _Iterator
from typing import MutableMapping as _MutableMapping
from typing import Type as _Type
from typing import TypeVar as _TypeVar

# third-party
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.logging import LoggerType as _LoggerType
from vcorelib.namespace import Namespace as _Namespace

# internal
from runtimepy.net.connection import Connection as _Connection
from runtimepy.task import PeriodicTask
from runtimepy.tui.mixin import TuiMixin

ConnectionMap = _MutableMapping[str, _Connection]
T = _TypeVar("T", bound=_Connection)
V = _TypeVar("V", bound=PeriodicTask)


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

    # Connection names.
    names: _Namespace

    # A signal that, when set, indicates the application to begin shutting
    # down.
    stop: _asyncio.Event

    # Configuration data that may be specified in a configuration file.
    config: _JsonObject

    tui: TuiMixin

    tasks: Dict[str, PeriodicTask]

    def with_new_logger(self, name: str) -> "AppInfo":
        """Get a copy of this AppInfo instance, but with a new logger."""

        return AppInfo(
            _getLogger(name),
            self.stack,
            self.connections,
            self.names,
            self.stop,
            self.config,
            self.tui,
            self.tasks,
        )

    def search(
        self,
        *names: str,
        pattern: str = ".*",
        kind: _Type[T] = _Connection,  # type: ignore
    ) -> _Iterator[T]:
        """
        Get all connections that are matching a naming convention or are
        specific kind (or both).
        """

        for name in self.names.search(*names, pattern=pattern):
            conn = self.connections[name]
            if isinstance(conn, kind):
                yield conn

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
