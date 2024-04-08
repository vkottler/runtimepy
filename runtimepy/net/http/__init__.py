"""
A module implementing an HTTP-message processing interface.
"""

# built-in
from typing import Iterator, Optional, cast

# third-party
from vcorelib.io import ByteFifo

# internal
from runtimepy.net.http.common import HeadersMixin
from runtimepy.net.http.state import HeaderProcessingState, T


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

        self.current_header: Optional[HeadersMixin] = None

    def ingest(
        self, data: bytes, kind: type[T]
    ) -> Iterator[tuple[T, Optional[bytes]]]:
        """Process a binary frame."""

        self.buffer.ingest(data)

        can_read_payload = True
        while self.buffer.size > 0 and can_read_payload:
            # Finish parsing header if necessary.
            if self.current_header is None:
                self.current_header = self.header.service(self.buffer, kind)

            # Read payload data.
            if self.current_header is not None:
                payload = None

                # Determine if any data payload is expected, and if so if we
                # have enough bytes to fully read it.
                payload_len = self.current_header.content_length
                can_read_payload = (
                    payload_len == 0 or self.buffer.size >= payload_len
                )
                if can_read_payload:
                    if payload_len > 0:
                        payload = self.buffer.pop(payload_len)
                    yield cast(T, self.current_header), payload
                    self.current_header = None
