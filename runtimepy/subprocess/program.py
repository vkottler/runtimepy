"""
A module implementing a peer program communication interface.
"""

# built-in
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

        while True:
            data: bytes = buffer.read(1)
            if not data:
                break

            # Process incoming messages.
            for msg in self.processor.messages(data):
                await self.process_json(msg)

    @classmethod
    async def run_standard(cls: Type[T], env: ChannelEnvironment) -> None:
        """Run this program using standard input and output."""

        peer = cls(env)
        peer.output = sys.stdout.buffer
        await peer.run(sys.stdin.buffer)
