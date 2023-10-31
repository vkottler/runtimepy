"""
A module implementing a TCP connection interface.
"""

# built-in
import asyncio as _asyncio
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

# internal
from runtimepy.net import sockname as _sockname
from runtimepy.net.connection import BinaryMessage as _BinaryMessage
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.connection import EchoConnection as _EchoConnection
from runtimepy.net.connection import NullConnection as _NullConnection
from runtimepy.net.manager import ConnectionManager as _ConnectionManager
from runtimepy.net.mixin import TransportMixin as _TransportMixin
from runtimepy.net.tcp.create import (
    TcpTransportProtocol,
    tcp_transport_protocol_backoff,
    try_tcp_transport_protocol,
)
from runtimepy.net.tcp.protocol import QueueProtocol

LOG = _getLogger(__name__)
T = _TypeVar("T", bound="TcpConnection")
ConnectionCallback = _Callable[[T], None]


class TcpConnection(_Connection, _TransportMixin):
    """A TCP connection interface."""

    # TCP connections send data directly without going through queues.
    uses_text_tx_queue = False
    uses_binary_tx_queue = False

    def __init__(self, transport: _Transport, protocol: QueueProtocol) -> None:
        """Initialize this TCP connection."""

        _TransportMixin.__init__(self, transport)

        # Re-assign with updated type information.
        self._transport: _Transport = transport
        self._set_protocol(protocol)

        super().__init__(_getLogger(self.logger_name("TCP ")))

        # Store connection-instantiation arguments.
        self._conn_kwargs: dict[str, _Any] = {}

    def _set_protocol(self, protocol: QueueProtocol) -> None:
        """Set a new protocol for this instance."""

        self._protocol = protocol
        self._protocol.conn = self

    async def _await_message(self) -> _Optional[_Union[_BinaryMessage, str]]:
        """Await the next message. Return None on error or failure."""

        data = await self._protocol.queue.get()
        if data is not None:
            self.metrics.rx.increment(len(data))
        return data

    def send_text(self, data: str) -> None:
        """Enqueue a text message to send."""
        self.send_binary(data.encode())

    def send_binary(self, data: _BinaryMessage) -> None:
        """Enqueue a binary message tos end."""
        self._transport.write(data)
        self.metrics.tx.increment(len(data))

    async def restart(self) -> bool:
        """
        Reset necessary underlying state for this connection to 'process'
        again.
        """

        def callback(transport_protocol: TcpTransportProtocol) -> None:
            """Callback if the socket creation succeeds."""

            self.set_transport(transport_protocol[0])
            self._set_protocol(transport_protocol[1])

        result = await try_tcp_transport_protocol(
            callback=callback, **self._conn_kwargs
        )
        return result is not None

    @classmethod
    async def create_connection(cls: _Type[T], **kwargs) -> T:
        """Create a TCP connection."""

        transport, protocol = await tcp_transport_protocol_backoff(**kwargs)
        inst = cls(transport, protocol)

        # Is there a better way to do this? We can't restart a server's side
        # of a connection (seems okay).
        inst._conn_kwargs = {**kwargs}

        return inst

    @classmethod
    @_asynccontextmanager
    async def serve(
        cls: _Type[T],
        callback: ConnectionCallback[T] = None,
        **kwargs,
    ) -> _AsyncIterator[_Any]:
        """Serve incoming connections."""

        class CallbackProtocol(QueueProtocol):
            """Protocol that calls the provided callback."""

            def connection_made(self, transport) -> None:
                """Save the transport reference and notify."""
                super().connection_made(transport)

                self.conn = cls(transport, self)
                if callback is not None:
                    callback(self.conn)

        eloop = _get_event_loop()
        server = await eloop.create_server(
            CallbackProtocol, family=_socket.AF_INET, **kwargs
        )
        async with server:
            for socket in server.sockets:
                LOG.info(
                    "Started TCP server listening on '%s'.", _sockname(socket)
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

            LOG.info("TCP Application starting.")
            await manager.manage(stop_sig)
            LOG.info("TCP Application stopped.")

        LOG.info("TCP Server closed.")

    @classmethod
    @_asynccontextmanager
    async def create_pair(cls: _Type[T]) -> _AsyncIterator[_Tuple[T, T]]:
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
            yield conn1, conn2

    async def close(self) -> None:
        """Close this connection."""
        self._transport.close()


class EchoTcpConnection(TcpConnection, _EchoConnection):
    """An echo connection for TCP."""


class NullTcpConnection(TcpConnection, _NullConnection):
    """A null TCP connection."""
