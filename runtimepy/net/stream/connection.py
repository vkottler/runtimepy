"""
A module implementing a connection interface for file streams (such as stdin
and stdout).
"""

# built-in
import asyncio as _asyncio
from logging import getLogger
import sys as _sys
from typing import IO, BinaryIO, Optional, TextIO, Type, TypeVar, Union

# third-party
from vcorelib.asyncio import normalize_eloop as _normalize_eloop

# internal
from runtimepy.net.connection import BinaryMessage as _BinaryMessage
from runtimepy.net.connection import Connection as _Connection
from runtimepy.net.connection import EchoConnection as _EchoConnection
from runtimepy.net.connection import NullConnection as _NullConnection

T = TypeVar("T", bound="StreamConnection")


class StreamConnection(_Connection):
    """A connection implementation for a stream reader and writer pair."""

    # Text queue structures for sending not necessary.
    uses_text_tx_queue = False

    def __init__(
        self,
        name: str,
        read: int,
        write: int = None,
        eloop: _asyncio.AbstractEventLoop = None,
    ) -> None:
        """Initialize this instance."""

        self._read = read
        self._write = write
        self.eloop = _normalize_eloop(eloop)

        # Register callbacks.
        self.eloop.add_reader(self._read, self._handle_read_signal)
        if self._write is not None:
            self.eloop.add_writer(self._write, self._handle_write_signal)

        super().__init__(getLogger(name))

    def _handle_read_signal(self) -> None:
        """TODO."""

    def _handle_write_signal(self) -> None:
        """TODO."""

    async def _await_message(self) -> Optional[Union[_BinaryMessage, str]]:
        """Await the next message. Return None on error or failure."""

        print("TODO")
        return None

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""
        return await self.process_text(data.decode())

    def send_text(self, data: str) -> None:
        """Enqueue a text message to send."""
        self.send_binary(data.encode())

    async def _send_binay_message(self, data: _BinaryMessage) -> None:
        """Send a binary message."""

        print(data)

    async def close(self) -> None:
        """Close this connection."""

        # Remove callbacks.
        self.eloop.remove_reader(self._read)
        if self._write is not None:
            self.eloop.remove_writer(self._write)


class EchoStreamConnection(StreamConnection, _EchoConnection):
    """An echo connection for streams."""


class NullStreamConnection(StreamConnection, _NullConnection):
    """A null connection for streams."""
