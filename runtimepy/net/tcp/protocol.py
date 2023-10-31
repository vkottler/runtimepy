"""
A module implementing a Protocol for TcpConnection.
"""

# built-in
from asyncio import BaseTransport as _BaseTransport
from asyncio import Protocol as _Protocol
from logging import getLogger as _getLogger
from typing import Optional as _Optional

# third-party
from vcorelib.logging import LoggerType as _LoggerType

# internal
from runtimepy.net.connection import BinaryMessage as _BinaryMessage
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.mixin import (
    BinaryMessageQueueMixin as _BinaryMessageQueueMixin,
)
from runtimepy.net.mixin import TransportMixin as _TransportMixin


class QueueProtocol(_BinaryMessageQueueMixin, _Protocol):
    """A simple streaming protocol that populates a message queue."""

    logger: _LoggerType
    conn: _Connection

    def data_received(self, data: _BinaryMessage) -> None:
        """Handle incoming data."""

        self.queue.put_nowait(data)
        self.queue_hwm = max(self.queue_hwm, self.queue.qsize())

    def connection_made(self, transport: _BaseTransport) -> None:
        """Log the connection establishment."""

        self.logger = _getLogger(
            _TransportMixin(transport).logger_name("TCP ")
        )
        self.logger.info("Connected.")

    def connection_lost(self, exc: _Optional[Exception]) -> None:
        """Log the disconnection."""

        msg = "Disconnected." if exc is None else f"Disconnected: '{exc}'."
        self.logger.info(msg)
        self.conn.disable("disconnected")
