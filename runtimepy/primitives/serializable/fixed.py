"""
A module implementing a fixed-size bytes serializable.
"""

# built-in
from copy import copy as _copy

# internal
from runtimepy.primitives.serializable.base import Serializable


class FixedChunk(Serializable):
    """A simple fixed-size serializable chunk."""

    def __init__(self, data: bytes, chain: Serializable = None) -> None:
        """Initialize this instance."""

        super().__init__(chain=chain)
        self.data = data
        self.size = len(self.data)

    def __str__(self) -> str:
        """Get this chunk as a string."""
        return self.data.decode()

    def _copy_impl(self) -> "FixedChunk":
        """Make a copy of this instance."""
        return FixedChunk(_copy(self.data))

    def __bytes__(self) -> bytes:
        """Get this serializable as a bytes instance."""
        return self.data

    def update(self, data: bytes, timestamp_ns: int = None) -> int:
        """Update this serializable from a bytes instance."""

        del timestamp_ns

        self.data = data
        self.size = len(self.data)
        return self.size
