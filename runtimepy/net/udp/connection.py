"""
A module implementing a UDP connection interface.
"""

# built-in
import asyncio as _asyncio
from asyncio import DatagramProtocol, DatagramTransport
from logging import getLogger
import socket as _socket
from typing import Any as _Any
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# third-party
from vcorelib.logging import LoggerType as _LoggerType

# internal
from runtimepy.net import get_free_socket_name
from runtimepy.net.connection import BinaryMessage, Connection

LOG = getLogger(__name__)


class UdpQueueProtocol(DatagramProtocol):
    """A simple UDP protocol that populates a message queue."""

    logger: _LoggerType

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
        self.logger.error(exc)


T = _TypeVar("T", bound="UdpConnection")


class UdpConnection(Connection):
    """A UDP connection interface."""

    def __init__(
        self, transport: DatagramTransport, protocol: UdpQueueProtocol
    ) -> None:
        """Initialize this UDP connection."""

        self._transport = transport
        self._protocol = protocol
        super().__init__(getLogger(self._logger_name()))
        self._protocol.logger = self.logger

    async def close(self) -> None:
        """Close this connection."""
        self._transport.close()

    def sendto(self, data: bytes, addr: _Any) -> None:
        """Send to a specific address."""
        self._transport.sendto(data, addr=addr)

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

        eloop = _asyncio.get_event_loop()

        transport: DatagramTransport
        (
            transport,
            protocol,
        ) = await eloop.create_datagram_endpoint(  # type: ignore
            UdpQueueProtocol, **kwargs
        )
        return cls(transport, protocol)

    @classmethod
    async def create_pair(cls: _Type[T]) -> _Tuple[T, T]:
        """Create a connection pair."""

        addr1 = get_free_socket_name(kind=_socket.SOCK_DGRAM)
        addr2 = get_free_socket_name(kind=_socket.SOCK_DGRAM)

        conn1 = await cls.create_connection(
            local_addr=addr1, remote_addr=addr2
        )
        conn2 = await cls.create_connection(
            local_addr=addr2, remote_addr=addr1
        )
        return conn1, conn2

    @property
    def local_address(self) -> _Tuple[str, int]:
        """Get the local address of this connection."""

        result = self._transport.get_extra_info("sockname")
        host: str = result[0]
        assert isinstance(host, str)
        port: int = result[1]
        assert isinstance(port, int)
        return host, port

    @property
    def remote_address(self) -> _Optional[_Tuple[str, int]]:
        """Get a possible remote address for this connection."""

        result = self._transport.get_extra_info("peername")
        if result is not None:
            host: str = result[0]
            assert isinstance(host, str)
            port: int = result[1]
            assert isinstance(port, int)
            return host, port
        return result

    def _logger_name(self) -> str:
        """Get a logger name for this connection."""

        host, port = self.local_address
        name = f"{host}:{port}"
        remote = self.remote_address
        if remote is not None:
            name += f" -> {remote[0]}:{remote[1]}"
        return name
