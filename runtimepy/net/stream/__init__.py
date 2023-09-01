"""
A module implementing a base, stream-oriented connection interface.
"""

# built-in
from io import BytesIO as _BytesIO
from typing import BinaryIO as _BinaryIO
from typing import Tuple, Type

# third-party
from vcorelib.io import ByteFifo

# internal
from runtimepy.net.connection import BinaryMessage
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.tcp.connection import TcpConnection
from runtimepy.net.udp.connection import UdpConnection
from runtimepy.primitives import Uint32, UnsignedInt


class PrefixedMessageConnection(_Connection):
    """
    A connection for handling inter-frame message size prefixes for some
    stream-oriented protocols.
    """

    message_length_kind: Type[UnsignedInt] = Uint32
    reading_header: bool

    def init(self) -> None:
        """Initialize this instance."""

        # Header parsing.
        self.buffer = ByteFifo()
        self.reading_header = True
        self.message_length_in = self.message_length_kind()
        self.prefix_size = self.message_length_in.size

        self.message_length_out = self.message_length_kind()

    def _send_message(
        self, data: BinaryMessage, addr: Tuple[str, int] = None
    ) -> None:
        """Underlying data send."""

        del addr
        self.send_binary(data)

    def send_message(
        self, data: BinaryMessage, addr: Tuple[str, int] = None
    ) -> None:
        """Handle inter-message prefixes for outgoing messages."""

        self.message_length_out.value = len(data)

        with _BytesIO() as stream:
            self.message_length_out.to_stream(
                stream, byte_order=self.byte_order
            )
            stream.write(data)
            self._send_message(stream.getvalue(), addr=addr)

    def send_message_str(
        self, data: str, addr: Tuple[str, int] = None
    ) -> None:
        """Convert a message to bytes before sending."""
        self.send_message(data.encode(), addr=addr)

    async def process_single(
        self, stream: _BinaryIO, addr: Tuple[str, int] = None
    ) -> bool:
        """Process a single message."""
        del stream
        del addr
        return True

    async def process_binary(
        self, data: bytes, addr: Tuple[str, int] = None
    ) -> bool:
        """Process an incoming message."""

        result = True

        self.buffer.ingest(data)

        can_continue = True
        while can_continue:
            # Read the message size.
            if self.reading_header:
                size = self.buffer.pop(self.prefix_size)
                if size is not None:
                    assert len(size) == self.prefix_size
                    self.message_length_in.update(
                        size, byte_order=self.byte_order
                    )
                    self.reading_header = False
                else:
                    can_continue = False

            # Read the message payload.
            else:
                message = self.buffer.pop(self.message_length_in.value)
                if message is not None:
                    # process message
                    with _BytesIO(message) as stream:
                        result &= await self.process_single(stream, addr=addr)
                    self.reading_header = True
                else:
                    can_continue = False

        return result


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


class StringMessageConnection(PrefixedMessageConnection):
    """A simple string-message sending and processing connection."""

    async def process_message(
        self, data: str, addr: Tuple[str, int] = None
    ) -> bool:
        """Process a string message."""

        del addr
        self.logger.info(data)
        return True

    async def process_single(
        self, stream: _BinaryIO, addr: Tuple[str, int] = None
    ) -> bool:
        """Process a single message."""

        return await self.process_message(stream.read().decode(), addr=addr)


class TcpStringMessageConnection(StringMessageConnection, TcpConnection):
    """A simple string-message sending and processing connection using TCP."""


class UdpStringMessageConnection(
    StringMessageConnection, UdpPrefixedMessageConnection
):
    """A simple string-message sending and processing connection using UDP."""
