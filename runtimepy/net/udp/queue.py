"""
A module implementing a simple queue-based UDP interface.
"""

# built-in
from asyncio import Queue

# internal
from runtimepy.net.udp.connection import UdpConnection

DatagramQueue = Queue[tuple[bytes, tuple[str, int]]]


class QueueUdpConnection(UdpConnection):
    """An echo connection for UDP."""

    datagrams: DatagramQueue

    def init(self) -> None:
        """Initialize this instance."""
        self.datagrams = Queue()

    async def process_datagram(
        self, data: bytes, addr: tuple[str, int]
    ) -> bool:
        """Process a datagram."""
        self.datagrams.put_nowait((data, addr))
        return True
