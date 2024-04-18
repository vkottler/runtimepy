"""
A module implementing a base, stream-oriented connection interface.
"""

# built-in
from io import BytesIO as _BytesIO
from typing import BinaryIO as _BinaryIO

# internal
from runtimepy.message import MessageProcessor
from runtimepy.net.connection import BinaryMessage
from runtimepy.net.connection import Connection as _Connection


class PrefixedMessageConnection(_Connection):
    """
    A connection for handling inter-frame message size prefixes for some
    stream-oriented protocols.
    """

    processor: MessageProcessor

    def init(self) -> None:
        """Initialize this instance."""

        # Header parsing.
        self.processor = MessageProcessor(byte_order=self.byte_order)

    def _send_message(
        self, data: BinaryMessage, addr: tuple[str, int] = None
    ) -> None:
        """Underlying data send."""

        del addr
        self.send_binary(data)

    def send_message(
        self, data: BinaryMessage, addr: tuple[str, int] = None
    ) -> None:
        """Handle inter-message prefixes for outgoing messages."""

        with _BytesIO() as stream:
            self.processor.encode(stream, data)
            self._send_message(stream.getvalue(), addr=addr)

    def send_message_str(
        self, data: str, addr: tuple[str, int] = None
    ) -> None:
        """Convert a message to bytes before sending."""
        self.send_message(data.encode(), addr=addr)

    async def process_single(
        self, stream: _BinaryIO, addr: tuple[str, int] = None
    ) -> bool:
        """Process a single message."""
        del stream
        del addr
        return True

    async def process_binary(
        self, data: bytes, addr: tuple[str, int] = None
    ) -> bool:
        """Process an incoming message."""

        result = True

        for message in self.processor.process(data):
            with _BytesIO(message) as stream:
                result &= await self.process_single(stream, addr=addr)

        return result
