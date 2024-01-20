"""
A module implementing a basic HTTP (multiple RFC's) connection interface.
"""

# built-in
from typing import Optional

# internal
from runtimepy.net.http import HttpMessageProcessor
from runtimepy.net.http.header import HttpHeader
from runtimepy.net.tcp.connection import TcpConnection as _TcpConnection


class HttpConnection(_TcpConnection):
    """A class implementing a basic HTTP interface."""

    processor: HttpMessageProcessor

    def init(self) -> None:
        """Initialize this instance."""

        self.processor = HttpMessageProcessor()

    async def process_request(
        self, header: HttpHeader, data: Optional[bytes]
    ) -> None:
        """Process an individual request."""

        del data
        header.log(self.logger)

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""

        for header, payload in self.processor.ingest(data):
            await self.process_request(header, payload)
            # HANDLE RESPONSE FROM ^'s RETURN

        return True
