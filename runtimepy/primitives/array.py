"""
A module for implementing arrays of arbitrary primitives.
"""

# built-in
from struct import pack as _pack
from struct import unpack as _unpack
from typing import BinaryIO as _BinaryIO
from typing import List as _List

# internal
from runtimepy.primitives import AnyPrimitive as _AnyPrimitive
from runtimepy.primitives.base import NETWORK_BYTE_ORDER as _NETWORK_BYTE_ORDER


class PrimitiveArray:
    """A class for managing primitives as arrays."""

    def __init__(
        self,
        *primitives: _AnyPrimitive,
        byte_order: str = _NETWORK_BYTE_ORDER,
    ) -> None:
        """Initialize this primitive array."""

        self._primitives: _List[_AnyPrimitive] = []
        self._format: str = byte_order
        self.size: int = 0

        # Add initial items.
        for item in primitives:
            self.add(item)

    def __getitem__(self, index: int) -> _AnyPrimitive:
        """Access underlying primitives by index."""
        return self._primitives[index]

    def add(self, primitive: _AnyPrimitive) -> int:
        """Add another primitive to manage."""

        self._primitives.append(primitive)
        self._format += primitive.kind.format
        self.size += primitive.kind.size
        return self.size

    def __bytes__(self) -> bytes:
        """Get this primitive array as a bytes instance."""

        return _pack(self._format, *(x.value for x in self._primitives))

    def to_stream(self, stream: _BinaryIO) -> int:
        """Write this array to a stream."""

        stream.write(bytes(self))
        return self.size

    def update(self, data: bytes) -> None:
        """Update primitive values from a bytes instance."""

        for primitive, item in zip(
            self._primitives, _unpack(self._format, data)
        ):
            primitive.value = item

    def from_stream(self, stream: _BinaryIO) -> int:
        """Update this array from a stream."""

        self.update(stream.read(self.size))
        return self.size
