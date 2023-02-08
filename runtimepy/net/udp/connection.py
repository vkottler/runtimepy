"""
A module implementing a UDP connection interface.
"""

from __future__ import annotations

# built-in
from abc import abstractmethod as _abstractmethod
import asyncio as _asyncio
from asyncio import DatagramProtocol as _DatagramProtocol
from asyncio import DatagramTransport as _DatagramTransport
from logging import getLogger
import socket as _socket
from typing import Tuple as _Tuple
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# third-party
from vcorelib.logging import LoggerType as _LoggerType

# internal
from runtimepy.net import IpHost, get_free_socket
from runtimepy.net.connection import BinaryMessage as _BinaryMessage
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.mixin import TransportMixin as _TransportMixin


class UdpQueueProtocol(_DatagramProtocol):
    """A simple UDP protocol that populates a message queue."""

    logger: _LoggerType

    def __init__(self) -> None:
        """Initialize this protocol."""
        self.queue: _asyncio.Queue[
            _Tuple[_BinaryMessage, _Tuple[str, int]]
        ] = _asyncio.Queue()

    def datagram_received(self, data: bytes, addr: _Tuple[str, int]) -> None:
        """Handle incoming data."""
        self.queue.put_nowait((data, addr))

    def error_received(self, exc: Exception) -> None:
        """Log any received errors."""
        self.logger.error(exc)


T = _TypeVar("T", bound="UdpConnection")


class UdpConnection(_Connection, _TransportMixin):
    """A UDP connection interface."""

    def __init__(
        self, transport: _DatagramTransport, protocol: UdpQueueProtocol
    ) -> None:
        """Initialize this UDP connection."""

        _TransportMixin.__init__(self, transport)

        # Re-assign with updated type information.
        self._transport: _DatagramTransport = transport

        self._protocol = protocol
        super().__init__(getLogger(self.logger_name()))
        self._protocol.logger = self.logger

    @_abstractmethod
    async def process_datagram(
        self, data: bytes, addr: _Tuple[str, int]
    ) -> bool:
        """Process a datagram."""

    def sendto(
        self, data: bytes, addr: _Union[IpHost, _Tuple[str, int]]
    ) -> None:
        """Send to a specific address."""
        self._transport.sendto(data, addr=addr)

    def send_text(self, data: str) -> None:
        """Enqueue a text message to send."""
        self._transport.sendto(data.encode(), addr=self.remote_address)

    def send_binary(self, data: _BinaryMessage) -> None:
        """Enqueue a binary message tos end."""
        self._transport.sendto(data, addr=self.remote_address)

    @classmethod
    async def create_connection(cls: _Type[T], **kwargs) -> T:
        """Create a UDP connection."""

        eloop = _asyncio.get_event_loop()

        transport: _DatagramTransport
        (
            transport,
            protocol,
        ) = await eloop.create_datagram_endpoint(UdpQueueProtocol, **kwargs)
        return cls(transport, protocol)

    @classmethod
    async def create_pair(cls: _Type[T]) -> _Tuple[T, T]:
        """Create a connection pair."""

        # On Windows, local UDP sockets can't even be connected until the
        # receiving port is bound.
        sock1 = get_free_socket(kind=_socket.SOCK_DGRAM)
        sock2 = get_free_socket(kind=_socket.SOCK_DGRAM)

        # On Windows, local address '0.0.0.0' (returned by getsockname()) isn't
        # valid to connect to.
        sock1.connect(("localhost", sock2.getsockname()[1]))
        sock2.connect(("localhost", sock1.getsockname()[1]))

        conn1 = await cls.create_connection(sock=sock1)
        conn2 = await cls.create_connection(sock=sock2)
        assert conn1.remote_address is not None
        assert conn2.remote_address is not None

        return conn1, conn2

    async def close(self) -> None:
        """Close this connection."""
        self._transport.close()

    async def _process_read(self) -> None:
        """Process incoming messages while this connection is active."""

        while self._enabled:
            # Attempt to get the next message.
            message = await self._cancelled_handler(
                self._protocol.queue.get(), "reading cancelled"
            )
            result = False

            if message is not None:
                result = await self.process_datagram(message[0], message[1])

            # If we failed to read a message, disable.
            if not result:
                self.disable("read processing error")
