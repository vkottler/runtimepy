"""
A module implementing a TCP connection interface.
"""

# built-in
import asyncio as _asyncio
from asyncio import BaseTransport as _BaseTransport
from asyncio import Protocol as _Protocol
from asyncio import Semaphore as _Semaphore
from asyncio import Transport as _Transport
from asyncio import get_event_loop as _get_event_loop
from contextlib import asynccontextmanager as _asynccontextmanager
from logging import getLogger as _getLogger
import socket as _socket
from typing import Any as _Any
from typing import AsyncIterator as _AsyncIterator
from typing import Callable as _Callable
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# third-party
from vcorelib.logging import LoggerType as _LoggerType

# internal
from runtimepy.net import sockname as _sockname
from runtimepy.net.connection import BinaryMessage as _BinaryMessage
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.manager import ConnectionManager as _ConnectionManager
from runtimepy.net.mixin import (
    BinaryMessageQueueMixin as _BinaryMessageQueueMixin,
)
from runtimepy.net.mixin import TransportMixin as _TransportMixin

LOG = _getLogger(__name__)


class QueueProtocol(_BinaryMessageQueueMixin, _Protocol):
    """A simple streaming protocol that populates a message queue."""

    logger: _LoggerType
    conn: _Connection

    def data_received(self, data: _BinaryMessage) -> None:
        """Handle incoming data."""
        self.queue.put_nowait(data)

    def connection_made(self, transport: _BaseTransport) -> None:
        """Log the connection establishment."""
        self.logger = _getLogger(_TransportMixin(transport).logger_name())
        self.logger.info("Connected.")

    def connection_lost(self, exc: _Optional[Exception]) -> None:
        """Log the disconnection."""
        msg = "Disconnected." if exc is None else f"Disconnected: '{exc}'."
        self.logger.info(msg)
        self.conn.disable("disconnected")


T = _TypeVar("T", bound="TcpConnection")
ConnectionCallback = _Callable[[T], None]


class TcpConnection(_Connection, _TransportMixin):
    """A TCP connection interface."""

    def __init__(self, transport: _Transport, protocol: QueueProtocol) -> None:
        """Initialize this TCP connection."""

        _TransportMixin.__init__(self, transport)

        # Re-assign with updated type information.
        self._transport: _Transport = transport

        self._protocol = protocol
        self._protocol.conn = self
        super().__init__(_getLogger(self.logger_name()))

    async def _await_message(self) -> _Optional[_Union[_BinaryMessage, str]]:
        """Await the next message. Return None on error or failure."""
        return await self._protocol.queue.get()

    def send_text(self, data: str) -> None:
        """Enqueue a text message to send."""
        self._transport.write(data.encode())

    def send_binary(self, data: _BinaryMessage) -> None:
        """Enqueue a binary message tos end."""
        self._transport.write(data)

    @classmethod
    async def create_connection(cls: _Type[T], **kwargs) -> T:
        """Create a TCP connection."""

        eloop = _get_event_loop()

        transport: _Transport
        transport, protocol = await eloop.create_connection(
            QueueProtocol, **kwargs
        )
        return cls(transport, protocol)

    @classmethod
    @_asynccontextmanager
    async def serve(
        cls: _Type[T], callback: ConnectionCallback[T] = None, **kwargs
    ) -> _AsyncIterator[_Any]:
        """Serve incoming connections."""

        class CallbackProtocol(QueueProtocol):
            """Protocol that calls the provided callback."""

            def connection_made(self, transport) -> None:
                """Save the transport reference and notify."""
                super().connection_made(transport)
                if callback is not None:
                    callback(
                        cls(  # pylint: disable=abstract-class-instantiated
                            transport, self
                        )
                    )

        eloop = _get_event_loop()
        server = await eloop.create_server(
            CallbackProtocol, family=_socket.AF_INET, **kwargs
        )
        async with server:
            for socket in server.sockets:
                LOG.info(
                    "Started server listening on '%s'.", _sockname(socket)
                )
            yield server

    @classmethod
    async def app(
        cls: _Type[T],
        stop_sig: _asyncio.Event,
        callback: ConnectionCallback[T] = None,
        serving_callback: _Callable[[_Any], None] = None,
        manager: _ConnectionManager = None,
        **kwargs,
    ) -> None:
        """Run an application that serves new connections."""

        if manager is None:
            manager = _ConnectionManager()

        def app_cb(conn: T) -> None:
            """Call the appication callback and enqueue the new connection."""
            if callback is not None:
                callback(conn)
            assert manager is not None
            manager.queue.put_nowait(conn)

        async with cls.serve(app_cb, **kwargs) as server:
            if serving_callback is not None:
                serving_callback(server)

            LOG.info("Application starting.")
            await manager.manage(stop_sig)
            LOG.info("Application stopped.")

        LOG.info("Server closed.")

    @classmethod
    async def create_pair(cls: _Type[T]) -> _Tuple[T, T]:
        """Create a connection pair."""

        cond = _Semaphore(0)
        conn1: _Optional[T] = None

        def callback(conn: T) -> None:
            """Signal the semaphore."""
            nonlocal conn1
            conn1 = conn
            cond.release()

        async with cls.serve(callback, port=0, backlog=1) as server:
            host = server.sockets[0].getsockname()
            conn2 = await cls.create_connection(host="localhost", port=host[1])
            await cond.acquire()

        assert conn1 is not None
        return conn1, conn2

    async def close(self) -> None:
        """Close this connection."""
        self._transport.close()
