"""
A module implementing a basic HTTP (multiple RFC's) connection interface.
"""

# internal
from runtimepy.net.tcp.connection import TcpConnection as _TcpConnection


class HttpConnection(_TcpConnection):
    """A class implementing a basic HTTP interface."""

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""

        print(data)

        return True
