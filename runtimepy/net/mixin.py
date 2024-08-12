"""
Various networking-related class utilities.
"""

from __future__ import annotations

# built-in
import asyncio as _asyncio
from socket import SocketType as _SocketType
from typing import Callable
from typing import Optional as _Optional
from typing import cast as _cast

# internal
from runtimepy.net import IpHost as _IpHost
from runtimepy.net import normalize_host as _normalize_host
from runtimepy.net.connection import BinaryMessage as _BinaryMessage
from runtimepy.net.mtu import ETHERNET_MTU, UDP_DEFAULT_MTU, host_discover_mtu


class BinaryMessageQueueMixin:
    """A mixin for adding a 'queue' attribute."""

    def __init__(self) -> None:
        """Initialize this protocol."""
        self.queue: _asyncio.Queue[_BinaryMessage] = _asyncio.Queue()


class TransportMixin:
    """A class simplifying evaluation of local and remote addresses."""

    _transport: _asyncio.BaseTransport
    remote_address: _Optional[_IpHost]

    def set_transport(self, transport: _asyncio.BaseTransport) -> None:
        """Set the transport for this instance."""

        self._transport = transport

        # Get the local address of this connection.
        self.local_address = _normalize_host(
            *self._transport.get_extra_info("sockname")
        )

        # A bug in the Windows implementation causes the 'addr' argument of
        # sendto to be required. Save a copy of the remote address (may be
        # None).
        self.remote_address = self._remote_address()

    def __init__(self, transport: _asyncio.BaseTransport) -> None:
        """Initialize this instance."""
        self.set_transport(transport)

    def mtu(
        self,
        probe_size: int = UDP_DEFAULT_MTU,
        fallback: int = ETHERNET_MTU,
        probe_create: Callable[[int], bytes] = bytes,
    ) -> int:
        """
        Get a maximum transmission unit for this connection. Underlying sockets
        must be connected for this to work.
        """

        assert (
            self.remote_address is not None
        ), "Not connected! Can't probe MTU."

        return host_discover_mtu(
            self.local_address,
            self.remote_address,
            probe_size,
            fallback,
            kind=self.socket.type,
            probe_create=probe_create,
        )

    @property
    def socket(self) -> _SocketType:
        """Get this instance's underlying socket."""
        return _cast(_SocketType, self._transport.get_extra_info("socket"))

    def _remote_address(self) -> _Optional[_IpHost]:
        """Get a possible remote address for this connection."""

        result = self._transport.get_extra_info("peername")
        addr = None
        if result is not None:
            addr = _normalize_host(*result)
        return addr

    def logger_name(self, prefix: str = "") -> str:
        """Get a logger name for this connection."""

        name = prefix + str(self.local_address)
        if self.remote_address is not None:
            name += f" -> {self.remote_address}"
        return name
