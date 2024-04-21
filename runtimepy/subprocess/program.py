"""
A module implementing a peer program communication interface.
"""

# built-in
import asyncio
from contextlib import asynccontextmanager, contextmanager
import logging
import os
import sys
from typing import AsyncIterator, BinaryIO, Iterator, Type, TypeVar

# internal
from runtimepy.net.arbiter.struct import RuntimeStruct
from runtimepy.subprocess.interface import RuntimepyPeerInterface

T = TypeVar("T", bound="PeerProgram")


class PeerProgram(RuntimepyPeerInterface):
    """A communication interface for peer programs."""

    json_output: BinaryIO
    stream_output: BinaryIO

    @contextmanager
    def streaming_events(self) -> Iterator[None]:
        """Stream events to the stream output."""

        with self.struct.env.channels.registered(self.stream_output):
            yield

    def write(self, data: bytes, addr: tuple[str, int] = None) -> None:
        """Write data."""

        del addr

        self.json_output.write(data)
        self.json_output.flush()
        self.stdout_metrics.increment(len(data))

    async def run(self, buffer: BinaryIO) -> None:
        """Run this peer program's main loop."""

        # Allow polling stdin.
        if hasattr(os, "set_blocking"):
            getattr(os, "set_blocking")(buffer.fileno(), False)

        while True:
            data: bytes = buffer.read(1)
            if data is None:
                await asyncio.sleep(self.poll_period_s)
                continue

            if not data:
                break

            # Process incoming messages.
            for msg in self.processor.messages(data):
                await self.process_json(msg)

    @classmethod
    def run_standard(
        cls: Type[T], struct: RuntimeStruct
    ) -> tuple[asyncio.Task[None], T]:
        """Run this program using standard input and output."""

        peer = cls(struct)
        peer.json_output = sys.stdout.buffer
        peer.stream_output = sys.stderr.buffer

        return asyncio.create_task(peer.run(sys.stdin.buffer)), peer

    @classmethod
    @asynccontextmanager
    async def running(
        cls: Type[T], struct: RuntimeStruct
    ) -> AsyncIterator[tuple[asyncio.Task[None], T]]:
        """
        Provide an interface for managed-context cleanup of the peer process.
        """

        task, peer = cls.run_standard(struct)

        # Set up logging.
        logger = logging.getLogger()
        logger.addHandler(peer.list_handler)

        peer.logger.info("Initialized.")

        try:
            yield task, peer
        finally:
            logger.removeHandler(peer.list_handler)
            task.cancel()
            await task
