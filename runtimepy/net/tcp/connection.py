"""
A module implementing a TCP connection interface.
"""

# built-in
import asyncio as _asyncio
from asyncio import Semaphore as _Semaphore
from asyncio import Transport as _Transport
from asyncio import get_event_loop as _get_event_loop
from contextlib import AsyncExitStack as _AsyncExitStack
from contextlib import asynccontextmanager as _asynccontextmanager
from logging import getLogger as _getLogger
from typing import Any as _Any
from typing import AsyncIterator as _AsyncIterator
from typing import Callable as _Callable
from typing import Optional as _Optional
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# internal
from runtimepy.net import sockname as _sockname
from runtimepy.net.backoff import ExponentialBackoff
from runtimepy.net.connection import BinaryMessage as _BinaryMessage
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.connection import EchoConnection as _EchoConnection
from runtimepy.net.connection import NullConnection as _NullConnection
from runtimepy.net.manager import ConnectionManager as _ConnectionManager
from runtimepy.net.mixin import TransportMixin as _TransportMixin
from runtimepy.net.ssl import handle_possible_ssl
from runtimepy.net.tcp.create import (
    TcpTransportProtocol,
    tcp_transport_protocol_backoff,
    try_tcp_transport_protocol,
)
from runtimepy.net.tcp.protocol import QueueProtocol

LOG = _getLogger(__name__)
T = _TypeVar("T", bound="TcpConnection")
V = _TypeVar("V", bound="TcpConnection")
ConnectionCallback = _Callable[[T], None]


class TcpConnection(_Connection, _TransportMixin):
    """A TCP connection interface."""

    # TCP connections send data directly without going through queues.
    uses_text_tx_queue = False
    uses_binary_tx_queue = False

    log_alias = "TCP"
    log_prefix = ""

    def __init__(
        self,
        transport: _Transport,
        protocol: QueueProtocol,
        **kwargs,
    ) -> None:
        """Initialize this TCP connection."""

        _TransportMixin.__init__(self, transport)

        # Re-assign with updated type information.
        self._transport: _Transport = transport
        self._set_protocol(protocol)

        super().__init__(
            _getLogger(self.logger_name(f"{self.log_alias} ")), **kwargs
        )

        # Store connection-instantiation arguments.
        self._conn_kwargs: dict[str, _Any] = {}

    def _set_protocol(self, protocol: QueueProtocol) -> None:
        """Set a new protocol for this instance."""

        self._protocol = protocol
        self._protocol.conn = self

    @classmethod
    def get_log_prefix(cls, is_ssl: bool = False) -> str:
        """Get a logging prefix for this instance."""

        # Default implementation doesn't handle this.
        del is_ssl

        return cls.log_prefix

    @property
    def is_ssl(self) -> bool:
        """Determine if this connection uses SSL."""
        return self._transport.get_extra_info("sslcontext") is not None

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
    async def create_connection(
        cls: type[T],
        backoff: ExponentialBackoff = None,
        markdown: str = None,
        **kwargs,
    ) -> T:
        """Create a TCP connection."""

        transport, protocol = await tcp_transport_protocol_backoff(
            backoff=backoff, **kwargs
        )
        inst = cls(transport, protocol, markdown=markdown)

        # Is there a better way to do this? We can't restart a server's side
        # of a connection (seems okay).
        inst._conn_kwargs = {**kwargs}

        return inst

    @classmethod
    @_asynccontextmanager
    async def serve(
        cls: type[T],
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

        server_kwargs = handle_possible_ssl(client=False, **kwargs)
        is_ssl = "ssl" in server_kwargs
        server = await eloop.create_server(CallbackProtocol, **server_kwargs)
        async with server:
            for socket in server.sockets:
                LOG.info(
                    "Started %s%s server listening on '%s%s'.",
                    "secure " if is_ssl else "",
                    cls.log_alias,
                    cls.get_log_prefix(is_ssl=is_ssl),
                    _sockname(socket),
                )
            yield server

    @classmethod
    async def app(
        cls: type[T],
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

            LOG.info("%s Application starting.", cls.log_alias)
            await manager.manage(stop_sig)
            LOG.info("%s Application stopped.", cls.log_alias)

        LOG.info("%s Server closed.", cls.log_alias)

    @classmethod
    @_asynccontextmanager
    async def create_pair(
        cls: type[T],
        peer: type[V] = None,
        serve_kwargs: dict[str, _Any] = None,
        connect_kwargs: dict[str, _Any] = None,
        host: str = "127.0.0.1",
    ) -> _AsyncIterator[tuple[V, T]]:
        """Create a connection pair."""

        cond = _Semaphore(0)
        server_conn: _Optional[V] = None

        def callback(conn: V) -> None:
            """Signal the semaphore."""
            nonlocal server_conn
            server_conn = conn
            cond.release()

        async with _AsyncExitStack() as stack:
            # Use the same class for the server end by default.
            if peer is None:
                peer = cls  # type: ignore
            assert peer is not None

            if serve_kwargs is None:
                serve_kwargs = {}

            server = await stack.enter_async_context(
                peer.serve(
                    callback,
                    host=host,
                    port=0,
                    backlog=1,
                    **serve_kwargs,
                )
            )

            if connect_kwargs is None:
                connect_kwargs = {}

            client = await cls.create_connection(
                host=host,
                port=server.sockets[0].getsockname()[1],
                **connect_kwargs,
            )
            await cond.acquire()

            assert server_conn is not None
            yield server_conn, client

    async def close(self) -> None:
        """Close this connection."""
        self._transport.close()


class EchoTcpConnection(TcpConnection, _EchoConnection):
    """An echo connection for TCP."""


class NullTcpConnection(TcpConnection, _NullConnection):
    """A null TCP connection."""
