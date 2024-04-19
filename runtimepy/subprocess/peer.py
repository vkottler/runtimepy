"""
A module implementing a runtimepy peer interface.
"""

# built-in
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Type, TypeVar

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.subprocess import spawn_exec, spawn_shell
from runtimepy.subprocess.interface import RuntimepyPeerInterface
from runtimepy.subprocess.protocol import RuntimepySubprocessProtocol

T = TypeVar("T", bound="RuntimepyPeer")


class RuntimepyPeer(RuntimepyPeerInterface):
    """A class implementing an interface for messaging peer subprocesses."""

    def __init__(self, protocol: RuntimepySubprocessProtocol) -> None:
        """Initialize this instance."""

        super().__init__(ChannelEnvironment())
        self.protocol = protocol

    async def _poll(self) -> None:
        """Poll input queues."""

        keep_going = True
        while keep_going:
            try:
                keep_going = await self.service_queues()
                if keep_going:
                    await asyncio.sleep(self.poll_period_s)
            except asyncio.CancelledError:
                keep_going = False

    @asynccontextmanager
    async def _context(self: T) -> AsyncIterator[T]:
        """A managed context for the peer."""

        # Register task that will poll queues.
        task = asyncio.create_task(self._poll())

        try:
            if await self.loopback():
                await self.wait_json({"meta": self.meta})
            yield self
        finally:
            task.cancel()
            await task

    @classmethod
    @asynccontextmanager
    async def shell(cls: Type[T], cmd: str) -> AsyncIterator[T]:
        """Create an instance from a shell command."""

        async with spawn_shell(
            cmd, stdout=asyncio.Queue(), stderr=asyncio.Queue()
        ) as proto:
            async with cls(proto)._context() as inst:
                yield inst

    @classmethod
    @asynccontextmanager
    async def exec(cls: Type[T], *args, **kwargs) -> AsyncIterator[T]:
        """Create an instance from comand-line arguments."""

        async with spawn_exec(
            *args, stdout=asyncio.Queue(), stderr=asyncio.Queue(), **kwargs
        ) as proto:
            async with cls(proto)._context() as inst:
                yield inst

    def write(self, data: bytes, addr: tuple[str, int] = None) -> None:
        """Write bytes via this interface."""
        del addr
        self.protocol.stdin.write(data)

    async def service_queues(self) -> bool:
        """Service data from peer."""

        keep_going = False

        # Forward stderr.
        if self.protocol.stderr_queue is not None:
            keep_going = True
            queue = self.protocol.stderr
            while not queue.empty():
                self.handle_stderr(queue.get_nowait())

        # Handle messages from stdout.
        if self.protocol.stdout_queue is not None:
            keep_going = True
            queue = self.protocol.stdout
            while not queue.empty():
                await self.handle_stdout(queue.get_nowait())

        return keep_going
