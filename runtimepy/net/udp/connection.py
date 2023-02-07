"""
A module implementing a UDP connection interface.
"""

# built-in
import asyncio as _asyncio
from asyncio import DatagramProtocol as _DatagramProtocol
from asyncio import DatagramTransport as _DatagramTransport
from logging import getLogger
import socket as _socket
from typing import Any as _Any
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# third-party
from vcorelib.logging import LoggerType as _LoggerType

# internal
from runtimepy.net import get_free_socket
from runtimepy.net.connection import BinaryMessage as _BinaryMessage
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.mixin import (
    BinaryMessageQueueMixin as _BinaryMessageQueueMixin,
)
from runtimepy.net.mixin import TransportMixin as _TransportMixin


class UdpQueueProtocol(_BinaryMessageQueueMixin, _DatagramProtocol):
    """A simple UDP protocol that populates a message queue."""

    logger: _LoggerType

    def datagram_received(self, data, addr) -> None:
        """Handle incoming data."""
        self.queue.put_nowait(data)

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

    def sendto(self, data: bytes, addr: _Any) -> None:
        """Send to a specific address."""
        self._transport.sendto(data, addr=addr)

    async def _send_text_message(self, data: str) -> None:
        """Send a text message."""
        self._transport.sendto(data.encode(), addr=self.remote_address)

    async def _send_binay_message(self, data: _BinaryMessage) -> None:
        """Send a binary message."""
        self._transport.sendto(data, addr=self.remote_address)

    async def _await_message(self) -> _Optional[_Union[_BinaryMessage, str]]:
        """Await the next message. Return None on error or failure."""
        return await self._protocol.queue.get()

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
