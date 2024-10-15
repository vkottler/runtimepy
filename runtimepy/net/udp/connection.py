"""
A module implementing a UDP connection interface.
"""

# built-in
from abc import abstractmethod as _abstractmethod
from asyncio import DatagramTransport as _DatagramTransport
from contextlib import suppress as _suppress
from logging import getLogger as _getLogger
import socket as _socket
from typing import Any as _Any
from typing import Optional as _Optional
from typing import TypeVar as _TypeVar

# internal
from runtimepy.net import IpHost, get_free_socket, normalize_host
from runtimepy.net.connection import BinaryMessage as _BinaryMessage
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.connection import EchoConnection as _EchoConnection
from runtimepy.net.connection import NullConnection as _NullConnection
from runtimepy.net.mixin import TransportMixin as _TransportMixin
from runtimepy.net.udp.create import (
    UdpTransportProtocol,
    try_udp_transport_protocol,
    udp_transport_protocol_backoff,
)
from runtimepy.net.udp.protocol import UdpQueueProtocol
from runtimepy.net.util import IpHostTuplelike

LOG = _getLogger(__name__)
T = _TypeVar("T", bound="UdpConnection")


class UdpConnection(_Connection, _TransportMixin):
    """A UDP connection interface."""

    # UDP connections send datagrams directly without going through queues.
    uses_text_tx_queue = False
    uses_binary_tx_queue = False

    # Simplify talkback implementations.
    latest_rx_address: _Optional[tuple[str, int]]

    log_alias = "UDP"

    def __init__(
        self,
        transport: _DatagramTransport,
        protocol: UdpQueueProtocol,
        **kwargs,
    ) -> None:
        """Initialize this UDP connection."""

        _TransportMixin.__init__(self, transport)
        if not self.remote_address:
            self.connected = False

        # Re-assign with updated type information.
        self._transport: _DatagramTransport = transport

        super().__init__(
            _getLogger(self.logger_name(f"{self.log_alias} ")), **kwargs
        )
        self._set_protocol(protocol)

        # Store connection-instantiation arguments.
        self._conn_kwargs: dict[str, _Any] = {}
        self.latest_rx_address = None

    def _set_protocol(self, protocol: UdpQueueProtocol) -> None:
        """Set a protocol instance for this connection."""

        self._protocol = protocol
        self._protocol.logger = self.logger
        self._protocol.conn = self

    def set_remote_address(self, addr: IpHost) -> None:
        """
        Set a new remote address. Note that this doesn't interact with or
        attempt to 'connect' the underlying socket. That should be done at
        creation time.
        """
        self.remote_address = addr
        self.logger = _getLogger(self.logger_name(f"{self.log_alias} "))
        self._protocol.logger = self.logger

    @_abstractmethod
    async def process_datagram(
        self, data: bytes, addr: tuple[str, int]
    ) -> bool:
        """Process a datagram."""

    def sendto(self, data: bytes, addr: IpHostTuplelike = None) -> None:
        """Send to a specific address."""

        try:
            self._transport.sendto(data, addr=addr)
            self.metrics.tx.increment(len(data))

        # Catch a bug in the underlying event loop implementation - we try to
        # send, but the underlying socket is gone (e.g. attribute is 'None').
        # This seems to be possible (but intermittent) when shutting down the
        # application.
        except AttributeError as exc:
            self.disable(str(exc))

    def send_text(self, data: str) -> None:
        """Enqueue a text message to send."""
        self.sendto(data.encode(), addr=self.remote_address)

    def send_binary(self, data: _BinaryMessage) -> None:
        """Enqueue a binary message to send."""
        self.sendto(data, addr=self.remote_address)

    async def restart(self) -> bool:
        """
        Reset necessary underlying state for this connection to 'process'
        again.
        """

        def callback(transport_protocol: UdpTransportProtocol) -> None:
            """Callback if the socket creation succeeds."""

            self.set_transport(transport_protocol[0])
            self._set_protocol(transport_protocol[1])

        result = await try_udp_transport_protocol(
            callback=callback, **self._conn_kwargs
        )
        return result is not None

    should_connect: bool = True

    @classmethod
    async def create_connection(
        cls: type[T], markdown: str = None, **kwargs
    ) -> T:
        """Create a UDP connection."""

        LOG.debug("kwargs: %s", kwargs)

        # Allows certain connections to have more sane defaults.
        connect = kwargs.pop("connect", cls.should_connect)

        # If the caller specifies a remote address but doesn't want a connected
        # socket, handle this after initial creation.
        remote_addr = None
        if not connect:
            if "remote_addr" in kwargs:
                remote_addr = kwargs.pop("remote_addr")

            # If only 'remote_addr' was specified, that's normally enough to
            # create the socket. Since we would have popped it, we now need
            # to specify a local address.
            if "local_addr" not in kwargs:
                kwargs["local_addr"] = ("0.0.0.0", 0)
                kwargs.setdefault("family", _socket.AF_INET)

        # Create the underlying connection.
        transport, protocol = await udp_transport_protocol_backoff(**kwargs)
        conn = cls(transport, protocol, markdown=markdown)
        conn._conn_kwargs = {**kwargs}

        # Set the remote address manually if necessary.
        if not connect and remote_addr is not None:
            conn.set_remote_address(normalize_host(*remote_addr))

        return conn

    @classmethod
    async def create_pair(cls: type[T]) -> tuple[T, T]:
        """Create a connection pair."""

        # On Windows, local UDP sockets can't even be connected until the
        # receiving port is bound.
        sock1 = get_free_socket(kind=_socket.SOCK_DGRAM)
        sock2 = get_free_socket(kind=_socket.SOCK_DGRAM)

        # On Windows, local address '0.0.0.0' (returned by getsockname()) isn't
        # valid to connect to.
        sock1.connect(("localhost", sock2.getsockname()[1]))
        sock2.connect(("localhost", sock1.getsockname()[1]))

        conn1 = await cls.create_connection(sock=sock1, connect=True)
        conn2 = await cls.create_connection(sock=sock2, connect=True)
        assert conn1.remote_address is not None
        assert conn2.remote_address is not None

        return conn1, conn2

    async def close(self) -> None:
        """Close this connection."""
        self._transport.close()

    async def _process_read(self) -> None:
        """Process incoming messages while this connection is active."""

        with _suppress(KeyboardInterrupt):
            while self._enabled:
                # Attempt to get the next message.
                message = await self._protocol.queue.get()
                result = False

                if message is not None:
                    data = message[0]
                    self.latest_rx_address = message[1]
                    result = await self.process_datagram(data, message[1])
                    self.metrics.rx.increment(len(data))

                # If we failed to read a message, disable.
                if not result:
                    self.disable("read processing error")


class EchoUdpConnection(UdpConnection, _EchoConnection):
    """An echo connection for UDP."""

    async def process_datagram(
        self, data: bytes, addr: tuple[str, int]
    ) -> bool:
        """Process a datagram."""

        self.sendto(data, addr=addr)
        return True


class NullUdpConnection(UdpConnection, _NullConnection):
    """A null UDP connection."""

    async def process_datagram(
        self, data: bytes, addr: tuple[str, int]
    ) -> bool:
        """Process a datagram."""
        return True
