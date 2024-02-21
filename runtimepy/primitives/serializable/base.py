"""
A module defining a base interface fore serializable objects.
"""

# built-in
from abc import ABC, abstractmethod
from copy import copy as _copy
from typing import BinaryIO as _BinaryIO
from typing import TypeVar

# third-party
from vcorelib import DEFAULT_ENCODING

# internal
from runtimepy.primitives.byte_order import (
    DEFAULT_BYTE_ORDER as _DEFAULT_BYTE_ORDER,
)
from runtimepy.primitives.byte_order import ByteOrder as _ByteOrder

T = TypeVar("T", bound="Serializable")


class Serializable(ABC):
    """An interface for serializable objects."""

    size: int

    def __init__(
        self,
        byte_order: _ByteOrder = _DEFAULT_BYTE_ORDER,
        chain: T = None,
    ) -> None:
        """Initialize this instance."""

        if not hasattr(self, "size"):
            self.size = 0

        self.byte_order = byte_order
        self.chain = chain

    def length(self) -> int:
        """Get the full length of this chain."""

        result = self.size
        if self.chain is not None:
            result += self.chain.length()
        return result

    def length_trace(self) -> str:
        """Get a length-tracing string for this instance."""

        current = f"{self.__class__.__name__}({self.size})"
        if self.chain is not None:
            current += " -> " + self.chain.length_trace()
        return current

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

    def copy_without_chain(self: T) -> T:
        """A method for copying instances without chain references."""

        orig = self._copy_impl()
        assert orig.chain is None
        orig.byte_order = self.byte_order
        return orig

    def __copy__(self: T) -> T:
        """Make a copy of this serializable."""

        result = self.copy_without_chain()

        if self.chain is not None:
            result.assign(self.chain.copy())

        return result

    def copy(self: T) -> T:
        """Create a copy of a serializable instance."""
        return _copy(self)

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

    def update_str(self, data: str) -> int:
        """Update this serializable from string data."""
        return self.update(data.encode(encoding=DEFAULT_ENCODING))

    def _from_stream(self, stream: _BinaryIO) -> int:
        """Update just this instance from a stream."""

        return self.update(stream.read(self.size))

    def from_stream(self, stream: _BinaryIO) -> int:
        """Update this serializable from a stream."""

        result = self._from_stream(stream)

        if self.chain is not None:
            result += self.chain.from_stream(stream)

        return result

    def assign(self, chain: T) -> int:
        """Assign a next serializable."""

        assert self.chain is None, self.chain
        self.chain = chain
        return self.chain.size

    def add_to_end(self, chain: T, array_length: int = None) -> int:
        """Add a new serializable to the end of this chain."""

        # Copy the chain element before it becomes part of the current chain
        # if an array is created.
        copy_base = None
        if array_length is not None:
            copy_base = chain.copy()

        size = self.end.assign(chain)

        # Add additional array elements as copies.
        if array_length is not None:
            assert copy_base is not None
            for _ in range(array_length - 1):
                size += self.end.assign(copy_base.copy())

        return size
