"""
A module implementing an application information interface.
"""

# built-in
import asyncio as _asyncio
from contextlib import AsyncExitStack as _AsyncExitStack
from typing import Iterator as _Iterator
from typing import MutableMapping as _MutableMapping
from typing import NamedTuple
from typing import Type as _Type
from typing import TypeVar as _TypeVar

# third-party
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.namespace import Namespace as _Namespace

# internal
from runtimepy.net.connection import Connection as _Connection

ConnectionMap = _MutableMapping[str, _Connection]
T = _TypeVar("T", bound=_Connection)


class AppInfo(NamedTuple):
    """References provided to network applications."""

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
