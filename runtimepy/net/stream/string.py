"""
A module implementing a string-message stream interface.
"""

# built-in
from typing import BinaryIO as _BinaryIO
from typing import Tuple

# internal
from runtimepy.net.stream.base import PrefixedMessageConnection


class StringMessageConnection(PrefixedMessageConnection):
    """A simple string-message sending and processing connection."""

    async def process_message(
        self, data: str, addr: Tuple[str, int] = None
    ) -> bool:
        """Process a string message."""

        del addr
        self.logger.info(data)
        return True

    async def process_single(
        self, stream: _BinaryIO, addr: Tuple[str, int] = None
    ) -> bool:
        """Process a single message."""

        return await self.process_message(stream.read().decode(), addr=addr)
