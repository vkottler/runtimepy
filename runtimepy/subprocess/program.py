"""
A module implementing a peer program communication interface.
"""

# built-in
import asyncio
import os
import sys
from typing import BinaryIO, Type, TypeVar

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.subprocess.interface import RuntimepyPeerInterface

T = TypeVar("T", bound="PeerProgram")


class PeerProgram(RuntimepyPeerInterface):
    """A communication interface for peer programs."""

    output: BinaryIO

    def write(self, data: bytes, addr: tuple[str, int] = None) -> None:
        """Write data."""

        del addr
        self.output.write(data)
        self.output.flush()

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
        cls: Type[T], env: ChannelEnvironment
    ) -> asyncio.Task[None]:
        """Run this program using standard input and output."""

        peer = cls(env)
        peer.output = sys.stdout.buffer
        return asyncio.create_task(peer.run(sys.stdin.buffer))
