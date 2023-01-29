"""
A module implementing a UDP connection interface.
"""

# built-in
import asyncio as _asyncio
from asyncio import DatagramProtocol, DatagramTransport
from logging import getLogger
from typing import Optional as _Optional
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# internal
from runtimepy.net.connection import BinaryMessage, Connection

LOG = getLogger(__name__)


class UdpQueueProtocol(DatagramProtocol):
    """A simple UDP protocol that populates a message queue."""

    def __init__(self) -> None:
        """Initialize this protocol."""

        self.queue: _asyncio.Queue[  # pylint: disable=unsubscriptable-object
            BinaryMessage
        ] = _asyncio.Queue()

    def datagram_received(self, data, addr) -> None:
        """Handle incoming data."""
        self.queue.put_nowait(data)

    def error_received(self, exc: Exception) -> None:
        """Log any received errors."""
        LOG.error(exc)


T = _TypeVar("T", bound="UdpConnection")


class UdpConnection(Connection):
    """A UDP connection interface."""

    def __init__(
        self, transport: DatagramTransport, protocol: UdpQueueProtocol
    ) -> None:
        """Initialize this UDP connection."""

        self._transport = transport
        self._protocol = protocol
        super().__init__(
            getLogger(
                (
                    f"{transport.get_extra_info('sockname')} -> "
                    f"{transport.get_extra_info('peername')}"
                )
            )
        )

    async def close(self) -> None:
        """Close this connection."""
        self._transport.close()

    async def _send_text_message(self, data: str) -> None:
        """Send a text message."""
        self._transport.sendto(data.encode())

    async def _send_binay_message(self, data: BinaryMessage) -> None:
        """Send a binary message."""
        self._transport.sendto(data)

    async def _await_message(self) -> _Optional[_Union[BinaryMessage, str]]:
        """Await the next message. Return None on error or failure."""
        return await self._protocol.queue.get()

    @classmethod
    async def create_connection(cls: _Type[T], **kwargs) -> T:
        """Create a UDP connection."""

        transport: DatagramTransport
        (
            transport,
            protocol,
        ) = await _asyncio.get_event_loop().create_connection(  # type: ignore
            UdpQueueProtocol, **kwargs
        )
        return cls(transport, protocol)
