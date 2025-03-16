"""
A module implementing a peer program communication interface.
"""

# built-in
import asyncio
from contextlib import asynccontextmanager, contextmanager, suppress
import logging
import os
import signal
import sys
from typing import AsyncIterator, BinaryIO, Iterator, Optional, Type, TypeVar

# third-party
from vcorelib.io import ARBITER
from vcorelib.io.types import JsonObject
from vcorelib.paths.context import tempfile

# internal
from runtimepy.metrics.channel import ChannelMetrics
from runtimepy.mixins.psutil import PsutilMixin
from runtimepy.net.arbiter import ConnectionArbiter
from runtimepy.net.arbiter.info import RuntimeStruct
from runtimepy.subprocess.interface import RuntimepyPeerInterface

T = TypeVar("T", bound="PeerProgram")
PROGRAM: Optional["PeerProgram"] = None


class PeerProgram(RuntimepyPeerInterface, PsutilMixin):
    """A communication interface for peer programs."""

    json_output: BinaryIO
    stream_output: BinaryIO
    stream_metrics: ChannelMetrics

    struct_type: Type[RuntimeStruct] = RuntimeStruct

    got_eof: asyncio.Event

    _singleton: Optional["PeerProgram"] = None

    @classmethod
    def singleton(cls: type[T]) -> T:
        """Get a shared single instance of a protocol for this class."""
        assert cls._singleton is not None
        return cls._singleton  # type: ignore

    @contextmanager
    def streaming_events(self) -> Iterator[None]:
        """Stream events to the stream output."""

        with self.struct.env.registered(
            self.stream_output, flush=True, channel=self.stream_metrics
        ):
            yield

    def write(self, data: bytes, addr: tuple[str, int] = None) -> None:
        """Write data."""

        del addr

        self.json_output.write(data)
        self.json_output.flush()
        self.stdout_metrics.increment(len(data))

    async def heartbeat_task(self) -> None:
        """Send a message heartbeat back and forth."""

        loop = asyncio.get_running_loop()
        prev_poll_time = loop.time()

        with suppress(asyncio.CancelledError):
            while not self.got_eof.is_set():
                # Perform heartbeat.
                if self._peer_env_event.is_set():
                    self.stderr_metrics.update(self.stream_metrics)

                    # Poll metrics.
                    curr = loop.time()
                    self.poll_psutil(curr - prev_poll_time)
                    prev_poll_time = curr

                    with suppress(AssertionError):
                        await self.process_command_queue()
                        await self.wait_json()

                await asyncio.sleep(self.poll_period_s * 10)

    async def io_task(self, buffer: BinaryIO) -> None:
        """Run this peer program's main loop."""

        self.got_eof.clear()

        # Allow polling stdin.
        if hasattr(os, "set_blocking"):
            getattr(os, "set_blocking")(buffer.fileno(), False)

        accumulator = 0

        with suppress(asyncio.CancelledError):
            while not self.got_eof.is_set():
                data: bytes = buffer.read(1)
                if data is None:
                    await asyncio.sleep(self.poll_period_s)
                    continue

                if not data:
                    break

                accumulator += 1

                # Process incoming messages.
                saw_msg = False
                for msg in self.processor.messages(data):
                    await self.process_json(msg)
                    saw_msg = True

                if saw_msg:
                    self.stdin_metrics.increment(accumulator)
                    accumulator = 0

        # Signal the end of input processing.
        self.got_eof.set()

    @classmethod
    def run_standard(
        cls: Type[T], name: str, config: JsonObject
    ) -> tuple[asyncio.Task[None], T]:
        """Run this program using standard input and output."""

        peer = cls(name, config)
        peer.json_output = sys.stdout.buffer
        peer.stream_output = sys.stderr.buffer
        peer.got_eof = asyncio.Event()
        peer.stream_metrics = ChannelMetrics()

        global PROGRAM  # pylint: disable=global-statement
        PROGRAM = peer
        assert cls._singleton is None
        cls._singleton = peer

        return asyncio.create_task(peer.io_task(sys.stdin.buffer)), peer

    async def main(self, argv: list[str]) -> None:
        """Program entry."""

        del argv

        with tempfile(suffix=".json") as config_path:
            arbiter = ConnectionArbiter(stop_sig=self.got_eof)
            ARBITER.encode(config_path, self.struct.config)
            await arbiter.load_configs([config_path])

        await arbiter.app()

    async def cleanup(self) -> None:
        """Runs when program 'running' context exits."""

    def pre_environment_exchange(self) -> None:
        """Perform early initialization tasks."""

    def struct_pre_finalize(self) -> None:
        """Configure struct before finalization."""
        self.init_psutil(self.struct.env)

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
        peer.logger.info("Logging initialized.")

        # Wait for environment exchange.
        peer.pre_environment_exchange()
        await peer._peer_env_event.wait()
        peer.logger.info("Environments exchanged.")

        # Start main loop.
        main_task = asyncio.create_task(peer.main(argv))
        peer.logger.info("Main started.")

        await peer.wait_json()
        heartbeat = asyncio.create_task(peer.heartbeat_task())

        try:
            with peer.streaming_events():
                yield io_task, main_task, peer
        finally:
            logger.removeHandler(peer.list_handler)
            for cancel in (io_task, main_task, heartbeat):
                cancel.cancel()
                await cancel

            await peer.cleanup()

    @classmethod
    async def run(
        cls: Type[T], name: str, config: JsonObject, argv: list[str]
    ) -> None:
        """Run the program."""

        # Don't respond to keyboard interrupt.
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        async with cls.running(name, config, argv) as (_, main_task, peer):
            with peer.log_time("Main task context", reminder=True):
                await main_task

    async def poll_handler(self) -> None:
        """Handle a 'poll' message."""

        self.struct.poll()
        self.poll_metrics()
