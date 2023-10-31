"""
A module implementing a DatagramProtocol for UdpConnection.
"""

# built-in
import asyncio as _asyncio
from asyncio import DatagramProtocol as _DatagramProtocol
from typing import Tuple as _Tuple

# third-party
from vcorelib.logging import LoggerType as _LoggerType

# internal
from runtimepy.net.connection import BinaryMessage as _BinaryMessage
from runtimepy.net.connection import Connection as _Connection


class UdpQueueProtocol(_DatagramProtocol):
    """A simple UDP protocol that populates a message queue."""

    logger: _LoggerType
    conn: _Connection

    def __init__(self) -> None:
        """Initialize this protocol."""

        self.queue: _asyncio.Queue[
            _Tuple[_BinaryMessage, _Tuple[str, int]]
        ] = _asyncio.Queue()
        self.queue_hwm: int = 0

    def datagram_received(self, data: bytes, addr: _Tuple[str, int]) -> None:
        """Handle incoming data."""

        self.queue.put_nowait((data, addr))
        self.queue_hwm = max(self.queue_hwm, self.queue.qsize())

    def error_received(self, exc: Exception) -> None:
        """Log any received errors."""

        self.logger.error(exc)

        # Most of the time this error occurs when sending to a loopback
        # destination (localhost) that is no longer listening.
        self.conn.disable(str(exc))
