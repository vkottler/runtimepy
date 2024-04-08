"""
A module implementing a variable-size bytes serializable, using an integer
primitive prefix to determine the size of the chunk portion.
"""

# built-in
from typing import BinaryIO as _BinaryIO
from typing import TypeVar

# internal
from runtimepy.primitives import Primitivelike, UnsignedInt, create
from runtimepy.primitives.byte_order import (
    DEFAULT_BYTE_ORDER as _DEFAULT_BYTE_ORDER,
)
from runtimepy.primitives.byte_order import ByteOrder as _ByteOrder
from runtimepy.primitives.serializable.base import Serializable
from runtimepy.primitives.serializable.fixed import FixedChunk

T = TypeVar("T", bound="PrefixedChunk")


class PrefixedChunk(Serializable):
    """A simple integer-prefixed chunk serializable."""

    def __init__(
        self,
        prefix: UnsignedInt,
        byte_order: _ByteOrder = _DEFAULT_BYTE_ORDER,
        chain: Serializable = None,
    ) -> None:
        """Initialize this instance."""

        super().__init__(byte_order=byte_order, chain=chain)

        # Validate prefix.
        assert prefix.kind.is_integer, prefix
        assert not prefix.kind.signed, prefix

        self.prefix = prefix
        self.chunk = FixedChunk(bytes(self.prefix.value))
        self._update_size()

    def __str__(self) -> str:
        """Get this chunk as a string."""
        return str(self.chunk)

    def update(self, data: bytes) -> int:
        """Update this serializable from a bytes instance."""

        size = self.chunk.update(data)
        self.prefix.value = size
        return self._update_size()

    def _update_size(self) -> int:
        """Update this instance's size."""

        assert self.prefix.value == self.chunk.size
        self.size = self.prefix.kind.size + self.prefix.value
        return self.size

    def _copy_impl(self) -> "PrefixedChunk":
        """Make a copy of this instance."""

        result = PrefixedChunk(self.prefix.copy())  # type: ignore
        result.chunk = self.chunk.copy()

        return result

    def __bytes__(self) -> bytes:
        """Get this serializable as a bytes instance."""

        return self.prefix.binary(byte_order=self.byte_order) + bytes(
            self.chunk
        )

    def _from_stream(self, stream: _BinaryIO) -> int:
        """Update just this instance from a stream."""

        self.chunk.update(
            stream.read(
                self.prefix.from_stream(stream, byte_order=self.byte_order)
            )
        )
        return self._update_size()

    @classmethod
    def create(
        cls: type[T],
        prefix: Primitivelike = "uint16",
        chain: Serializable = None,
    ) -> T:
        """Create a prefixed chunk."""

        return cls(create(prefix), chain=chain)  # type: ignore
