"""
Various networking-related class utilities.
"""

from __future__ import annotations

# built-in
import asyncio as _asyncio
from typing import Optional as _Optional

# internal
from runtimepy.net import IpHost as _IpHost
from runtimepy.net import normalize_host as _normalize_host
from runtimepy.net.connection import BinaryMessage as _BinaryMessage


class BinaryMessageQueueMixin:
    """A mixin for adding a 'queue' attribute."""

    def __init__(self) -> None:
        """Initialize this protocol."""
        self.queue: _asyncio.Queue[_BinaryMessage] = _asyncio.Queue()


class TransportMixin:
    """A class simplifying evaluation of local and remote addresses."""

    _transport: _asyncio.BaseTransport

    def __init__(self, transport: _asyncio.BaseTransport) -> None:
        """Initialize this instance."""

        self._transport = transport

        # Get the local address of this connection.
        self.local_address = _normalize_host(
            *self._transport.get_extra_info("sockname")
        )

        # A bug in the Windows implementation causes the 'addr' argument of
        # sendto to be required. Save a copy of the remote address (may be
        # None).
        self.remote_address = self._remote_address()

    def _remote_address(self) -> _Optional[_IpHost]:
        """Get a possible remote address for this connection."""

        result = self._transport.get_extra_info("peername")
        addr = None
        if result is not None:
            addr = _normalize_host(*result)
        return addr

    def logger_name(self) -> str:
        """Get a logger name for this connection."""

        name = str(self.local_address)
        if self.remote_address is not None:
            name += f" -> {self.remote_address}"
        return name
