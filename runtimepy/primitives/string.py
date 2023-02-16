"""
A module implementing integer-prefixed string reading and writing.
"""

# built-in
from typing import BinaryIO as _BinaryIO
from typing import Type as _Type

# internal
from runtimepy.primitives.base import Primitive as _Primitive
from runtimepy.primitives.byte_order import (
    DEFAULT_BYTE_ORDER as _DEFAULT_BYTE_ORDER,
)
from runtimepy.primitives.byte_order import ByteOrder as _ByteOrder
from runtimepy.primitives.int import Uint16 as _Uint16


class StringPrimitive:
    """A class implementing a string-primitive interface."""

    def __init__(
        self,
        value: str = "",
        kind: _Type[_Primitive[int]] = _Uint16,
        byte_order: _ByteOrder = _DEFAULT_BYTE_ORDER,
    ) -> None:
        """Initialize this string primitive."""

        assert kind.kind.is_integer
        self._value = value
        self._size = kind(len(self._value))
        self.byte_order = byte_order

    @property
    def value(self) -> str:
        """Get the value of this string."""
        return self._value

    def set(self, value: str) -> None:
        """Set a new value for the underlying string."""
        self._value = value
        self._size.value = len(self._value)

    @property
    def size(self) -> int:
        """Get the overall size of this string primitive."""
        return self._size.value + self._size.size

    def write(self, stream: _BinaryIO) -> int:
        """Write this string's size and value to the stream."""
        size = self._size.to_stream(stream, byte_order=self.byte_order)
        return size + stream.write(self._value.encode())

    def read(self, stream: _BinaryIO) -> str:
        """Read a string from the stream."""
        self._value = stream.read(
            self._size.from_stream(stream, byte_order=self.byte_order)
        ).decode()
        return self._value
