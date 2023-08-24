"""
A module defining an interface for serializable objects.
"""

# built-in
from abc import ABC, abstractmethod
from copy import copy as _copy
from typing import BinaryIO as _BinaryIO
from typing import TypeVar

T = TypeVar("T", bound="Serializable")


class Serializable(ABC):
    """An interface for serializable objects."""

    size: int

    def __init__(self, chain: T = None) -> None:
        """Initialize this instance."""

        if not hasattr(self, "size"):
            self.size = 0
        self.chain = chain

    def length(self) -> int:
        """Get the full length of this chain."""

        result = self.size
        if self.chain is not None:
            result += self.chain.length()
        return result

    @property
    def end(self) -> "Serializable":
        """Get the end of this chain."""

        result = self
        if self.chain is not None:
            result = self.chain.end
        return result

    @abstractmethod
    def _copy_impl(self: T) -> T:
        """Make a copy of this instance."""

    def __copy__(self: T) -> T:
        """Make a copy of this serializable."""

        result = self._copy_impl()

        if self.chain is not None:
            result.assign(self.chain.copy())

        return result

    def copy(self: T) -> T:
        """Create a copy of a serializable instance."""
        return _copy(self)

    def replace(self, serializable: T) -> None:
        """Replace this node in the chain."""

        if self.chain is not None:
            serializable.assign(self.chain)
            self.chain = None

    @abstractmethod
    def __bytes__(self) -> bytes:
        """Get this serializable as a bytes instance."""

    def to_stream(self, stream: _BinaryIO) -> int:
        """Write this serializable to a stream."""

        stream.write(bytes(self))
        result = self.size

        if self.chain is not None:
            result += self.chain.to_stream(stream)

        return result

    @abstractmethod
    def update(self, data: bytes) -> int:
        """Update this serializable from a bytes instance."""

    def from_stream(self, stream: _BinaryIO) -> int:
        """Update this serializable from a stream."""

        result = self.update(stream.read(self.size))

        if self.chain is not None:
            result += self.chain.from_stream(stream)

        return result

    def assign(self, chain: T) -> None:
        """Assign a next serializable."""

        assert self.chain is None, self.chain
        self.chain = chain

    def add_to_end(self, chain: T) -> None:
        """Add a new serializable to the end of this chain."""

        self.end.assign(chain)


class FixedChunk(Serializable):
    """A simple fixed-size serializable chunk."""

    def __init__(self, data: bytes, chain: Serializable = None) -> None:
        """Initialize this instance."""

        super().__init__(chain=chain)
        assert data
        self.data = data
        self.size = len(self.data)

    def _copy_impl(self) -> "FixedChunk":
        """Make a copy of this instance."""
        return FixedChunk(self.data)

    def __bytes__(self) -> bytes:
        """Get this serializable as a bytes instance."""
        return self.data

    def update(self, data: bytes) -> int:
        """Update this serializable from a bytes instance."""

        assert len(data) == self.size
        self.data = data
        return self.size
