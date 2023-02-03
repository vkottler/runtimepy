"""
A module implementing a TCP connection interface.
"""

# built-in
from asyncio import Protocol as _Protocol
from asyncio import Transport as _Transport
from logging import getLogger as _getLogger
from typing import Optional as _Optional
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# internal
from runtimepy.net.connection import BinaryMessage as _BinaryMessage
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.mixin import (
    BinaryMessageQueueMixin as _BinaryMessageQueueMixin,
)
from runtimepy.net.mixin import TransportMixin as _TransportMixin


class QueueProtocol(_BinaryMessageQueueMixin, _Protocol):
    """A simple streaming protocol that populates a message queue."""

    def data_received(self, data) -> None:
        """Handle incoming data."""
        self.queue.put_nowait(data)


T = _TypeVar("T", bound="TcpConnection")


class TcpConnection(_Connection, _TransportMixin):
    """A TCP connection interface."""

    def __init__(self, transport: _Transport, protocol: QueueProtocol) -> None:
        """Initialize this TCP connection."""

        _TransportMixin.__init__(self, transport)

        # Re-assign with updated type information.
        self._transport: _Transport = transport

        self._protocol = protocol
        super().__init__(_getLogger(self._logger_name()))

    async def _await_message(self) -> _Optional[_Union[_BinaryMessage, str]]:
        """Await the next message. Return None on error or failure."""
        return await self._protocol.queue.get()

    async def _send_text_message(self, data: str) -> None:
        """Send a text message."""
        self._transport.write(data.encode())

    async def _send_binay_message(self, data: _BinaryMessage) -> None:
        """Send a binary message."""
        self._transport.write(data)
