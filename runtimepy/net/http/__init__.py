"""
A module implementing an HTTP-message processing interface.
"""

# built-in
from typing import Iterator, Optional, Tuple

# third-party
from vcorelib.io import ByteFifo

# internal
from runtimepy.net.http.header import HttpHeader
from runtimepy.net.http.state import HeaderProcessingState


class HttpMessageProcessor:
    """
    A class implementing HTTP/1.1 (RFC 9112) message processing from a byte
    stream.
    """

    def __init__(self) -> None:
        """Initialize this instance."""

        # Header parsing.
        self.buffer = ByteFifo()
        self.header = HeaderProcessingState.create()

    def ingest(
        self, data: bytes
    ) -> Iterator[Tuple[HttpHeader, Optional[bytes]]]:
        """Process a binary frame."""

        self.buffer.ingest(data)

        while self.buffer.size:
            header = self.header.service(self.buffer)
            if header is not None:
                payload = None
                if self.buffer.size:
                    payload = self.buffer.pop(self.buffer.size)
                yield header, payload
