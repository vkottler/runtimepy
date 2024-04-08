"""
A module implementing a basic WebSocket connection factory that can be
extended.
"""

# built-in
import asyncio as _asyncio
from typing import Generic as _Generic
from typing import TypeVar as _TypeVar

# internal
from runtimepy.net.arbiter.base import ServerTask as _ServerTask
from runtimepy.net.arbiter.factory import (
    ConnectionFactory as _ConnectionFactory,
)
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.manager import ConnectionManager as _ConnectionManager
from runtimepy.net.websocket.connection import (
    WebsocketConnection as _WebsocketConnection,
)

T = _TypeVar("T", bound=_WebsocketConnection)


class WebsocketConnectionFactory(_ConnectionFactory, _Generic[T]):
    """A class implementing a basic WebSocket connection factory."""

    kind: type[T]

    async def client(self, name: str, *args, **kwargs) -> _Connection:
        """Create a client connection."""

        del name
        return await self.kind.create_connection(*args, **kwargs)

    async def server_task(
        self,
        stop_sig: _asyncio.Event,
        manager: _ConnectionManager,
        started_sem: _asyncio.Semaphore,
        *args,
        **kwargs,
    ) -> _ServerTask:
        """Create a task that will run a connection server."""

        assert not [*args], "Only keyword arguments are used!"
        return self.kind.app(
            stop_sig,
            serving_callback=lambda _: started_sem.release(),
            manager=manager,
            **kwargs,
        )
