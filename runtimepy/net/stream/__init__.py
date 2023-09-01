"""
A module aggregating stream-oriented connection interfaces.
"""

# built-in
from typing import BinaryIO as _BinaryIO
from typing import Tuple

# internal
from runtimepy.net.connection import BinaryMessage
from runtimepy.net.stream.base import PrefixedMessageConnection
from runtimepy.net.stream.string import StringMessageConnection
from runtimepy.net.tcp.connection import TcpConnection
from runtimepy.net.udp.connection import UdpConnection

__all__ = [
    "PrefixedMessageConnection",
    "StringMessageConnection",
    "TcpPrefixedMessageConnection",
    "UdpPrefixedMessageConnection",
    "EchoMessageConnection",
    "EchoTcpMessageConnection",
    "EchoUdpMessageConnection",
    "TcpStringMessageConnection",
    "UdpStringMessageConnection",
]


class TcpPrefixedMessageConnection(PrefixedMessageConnection, TcpConnection):
    """A TCP implementation for size-prefixed messages."""


class UdpPrefixedMessageConnection(PrefixedMessageConnection, UdpConnection):
    """A UDP implementation for size-prefixed messages."""

    async def process_datagram(
        self, data: bytes, addr: Tuple[str, int]
    ) -> bool:
        """Process a datagram."""

        return await self.process_binary(data, addr=addr)

    def _send_message(
        self, data: BinaryMessage, addr: Tuple[str, int] = None
    ) -> None:
        """Underlying data send."""

        self.sendto(data, addr=addr)


class EchoMessageConnection(PrefixedMessageConnection):
    """A connection that just echoes what it was sent."""

    async def process_single(
        self, stream: _BinaryIO, addr: Tuple[str, int] = None
    ) -> bool:
        """Process a single message."""

        self.send_message(stream.read(), addr=addr)
        return True


class EchoTcpMessageConnection(
    TcpPrefixedMessageConnection, EchoMessageConnection
):
    """A connection that just echoes what it was sent."""


class EchoUdpMessageConnection(
    UdpPrefixedMessageConnection, EchoMessageConnection
):
    """A connection that just echoes what it was sent."""


class TcpStringMessageConnection(StringMessageConnection, TcpConnection):
    """A simple string-message sending and processing connection using TCP."""


class UdpStringMessageConnection(
    StringMessageConnection, UdpPrefixedMessageConnection
):
    """A simple string-message sending and processing connection using UDP."""
