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

    @asynccontextmanager
    async def _context(self: T) -> AsyncIterator[T]:
        """A managed context for the peer."""

        if await self.loopback():
            await self.wait_json({"meta": self.meta})
        try:
            yield self
        finally:
            # Change this at some point?
            self.send_json({"command": "exit"})

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
        self.protocol.stdin.write(data)

    async def service_queues(self) -> None:
        """Service data from peer."""

        # Forward stderr.
        queue = self.protocol.stderr
        while not queue.empty():
            self.handle_stderr(queue.get_nowait())

        # Handle messages from stdout.
        queue = self.protocol.stdout
        while not queue.empty():
            await self.handle_stdout(queue.get_nowait())
