"""
A module implementing a basic TCP connection factory that can be extended.
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
from runtimepy.net.tcp.connection import TcpConnection as _TcpConnection

T = _TypeVar("T", bound=_TcpConnection)


class TcpConnectionFactory(_ConnectionFactory, _Generic[T]):
    """A class implementing a basic TCP connection factory."""

    kind: type[T]

    async def client(self, name: str, *args, **kwargs) -> _Connection:
        """Create a client connection."""

        del name
        assert not [*args], "Only keyword arguments are used!"
        return await self.kind.create_connection(**kwargs)

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
            manager=manager,
            serving_callback=lambda _: started_sem.release(),
            **kwargs,
        )
