"""
A module implementing a message-stream processing interface.
"""

# built-in
from io import BytesIO as _BytesIO
from json import dumps, loads
from typing import Any
from typing import Iterator as _Iterator

# third-party
from vcorelib.io import ByteFifo

# internal
from runtimepy.primitives import Uint32, UnsignedInt
from runtimepy.primitives.byte_order import DEFAULT_BYTE_ORDER, ByteOrder

JsonMessage = dict[str, Any]


class MessageProcessor:
    """A class for parsing size-delimited messages."""

    message_length_kind: type[UnsignedInt] = Uint32

    def __init__(self, byte_order: ByteOrder = DEFAULT_BYTE_ORDER) -> None:
        """Initialize this instance."""

        self.byte_order = byte_order

        # Header parsing.
        self.buffer = ByteFifo()
        self.reading_header = True
        self.message_length_in = self.message_length_kind()
        self.prefix_size = self.message_length_in.size

        self.message_length_out = self.message_length_kind()

    def encode(self, stream: _BytesIO, data: bytes | str) -> None:
        """Encode a message to a stream."""

        if isinstance(data, str):
            data = data.encode()

        self.message_length_out.value = len(data)
        self.message_length_out.to_stream(stream, byte_order=self.byte_order)
        stream.write(data)

    def encode_json(self, stream: _BytesIO, data: JsonMessage) -> None:
        """Encode a message as JSON."""
        self.encode(stream, dumps(data, separators=(",", ":")))

    def messages(self, data: bytes) -> _Iterator[JsonMessage]:
        """Iterate over incoming messages."""

        for message in self.process(data):
            yield loads(message.decode())

    def process(self, data: bytes) -> _Iterator[bytes]:
        """Process an incoming message."""

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
                    yield message
                    self.reading_header = True
                else:
                    can_continue = False
