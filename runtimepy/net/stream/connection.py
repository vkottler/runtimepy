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

IOStream = Union[TextIO, BinaryIO, IO[bytes]]
T = TypeVar("T", bound="StreamConnection")


class StreamConnection(_Connection):
    """A connection implementation for a stream reader and writer pair."""

    # Text queue structures for sending not necessary.
    uses_text_tx_queue = False

    def __init__(
        self,
        name: str,
        reader: _asyncio.StreamReader,
        writer: _asyncio.StreamWriter = None,
    ) -> None:
        """Initialize this instance."""

        self._reader = reader
        self._writer = writer
        super().__init__(getLogger(name))

    async def _await_message(self) -> Optional[Union[_BinaryMessage, str]]:
        """Await the next message. Return None on error or failure."""
        return await self._reader.readline()

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""
        return await self.process_text(data.decode())

    def send_text(self, data: str) -> None:
        """Enqueue a text message to send."""
        self.send_binary(data.encode())

    async def _send_binay_message(self, data: _BinaryMessage) -> None:
        """Send a binary message."""

        assert self._writer is not None
        self._writer.write(data)
        await self._writer.drain()

    async def close(self) -> None:
        """Close this connection."""

        if self._writer is not None:
            # Write EOF if it's supported.
            if self._writer.can_write_eof():
                self._writer.write_eof()

            # Write all remaining data.
            await self._writer.drain()

            # Close the writing end.
            self._writer.close()
            await self._writer.wait_closed()

    @classmethod
    async def create(
        cls: Type[T],
        read: IOStream = _sys.stdin,
        write: Optional[IOStream] = _sys.stdout,
        eloop: _asyncio.AbstractEventLoop = None,
        name: str = "stdio",
    ) -> T:
        """Create a stdio connection."""

        eloop = _normalize_eloop(eloop)

        # Connect a stream-reader and protocol instance to the read stream.
        reader = _asyncio.StreamReader()
        await eloop.connect_read_pipe(
            lambda: _asyncio.StreamReaderProtocol(reader), read
        )

        writer = None
        if write is not None:
            # Create the writer.
            transport, protocol = await eloop.connect_write_pipe(
                _asyncio.streams.FlowControlMixin, write
            )
            writer = _asyncio.StreamWriter(transport, protocol, reader, eloop)

        return cls(name, reader, writer=writer)


class EchoStreamConnection(StreamConnection, _EchoConnection):
    """An echo connection for streams."""


class NullStreamConnection(StreamConnection, _NullConnection):
    """A null connection for streams."""
