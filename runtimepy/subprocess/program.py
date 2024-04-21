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

# third-party
from vcorelib.io.types import JsonObject

# internal
from runtimepy.net.arbiter.struct import RuntimeStruct, SampleStruct
from runtimepy.subprocess.interface import RuntimepyPeerInterface

T = TypeVar("T", bound="PeerProgram")


class PeerProgram(RuntimepyPeerInterface):
    """A communication interface for peer programs."""

    json_output: BinaryIO
    stream_output: BinaryIO

    struct_type: Type[RuntimeStruct] = SampleStruct

    @contextmanager
    def streaming_events(self) -> Iterator[None]:
        """Stream events to the stream output."""

        with self.struct.env.channels.registered(
            self.stream_output, flush=True
        ):
            yield

    def write(self, data: bytes, addr: tuple[str, int] = None) -> None:
        """Write data."""

        del addr

        self.json_output.write(data)
        self.json_output.flush()
        self.stdout_metrics.increment(len(data))

    async def io_task(self, buffer: BinaryIO) -> None:
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
        cls: Type[T], name: str, config: JsonObject
    ) -> tuple[asyncio.Task[None], T]:
        """Run this program using standard input and output."""

        peer = cls(name, config)
        peer.json_output = sys.stdout.buffer
        peer.stream_output = sys.stderr.buffer

        return asyncio.create_task(peer.io_task(sys.stdin.buffer)), peer

    async def main(self, argv: list[str]) -> None:
        """Program entry."""

    async def cleanup(self) -> None:
        """Runs when program 'running' context exits."""

    @classmethod
    @asynccontextmanager
    async def running(
        cls: Type[T], name: str, config: JsonObject, argv: list[str]
    ) -> AsyncIterator[tuple[asyncio.Task[None], asyncio.Task[None], T]]:
        """
        Provide an interface for managed-context cleanup of the peer process.
        """

        io_task, peer = cls.run_standard(name, config)

        # Set up logging.
        logger = logging.getLogger()
        logger.addHandler(peer.list_handler)

        peer.logger.info("Initialized.")

        # Wait for environment exchange.
        await peer._peer_env_event.wait()
        peer.logger.info("Environments exchanged.")

        # Start main loop.
        main_task = asyncio.create_task(peer.main(argv))
        peer.logger.info("Main started.")

        try:
            yield io_task, main_task, peer
        finally:
            logger.removeHandler(peer.list_handler)
            for cancel in (io_task, main_task):
                cancel.cancel()
                await cancel

            await peer.cleanup()

    @classmethod
    async def run(
        cls: Type[T], name: str, config: JsonObject, argv: list[str]
    ) -> None:
        """Run the program."""

        async with cls.running(name, config, argv) as (io_task, main_task, _):
            await main_task
            await io_task
