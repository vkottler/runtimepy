"""
A module implementing a base, primitive-type storage entity.
"""

# built-in
from io import BytesIO as _BytesIO
from math import isclose as _isclose
from struct import pack as _pack
from struct import unpack as _unpack
from typing import BinaryIO as _BinaryIO
from typing import Generic as _Generic
from typing import TypeVar as _TypeVar

# internal
from runtimepy.primitives.type import PrimitiveTypelike as _PrimitiveTypelike
from runtimepy.primitives.type import normalize as _normalize

T = _TypeVar("T", bool, int, float)


class Primitive(_Generic[T]):
    """A simple class for storing and underlying primitive value."""

    # Use network byte-order by default.
    byte_order = "!"

    def __init__(self, kind: _PrimitiveTypelike, value: T = None) -> None:
        """Initialize this primitive."""

        assert kind is not None
        self.kind = _normalize(kind)
        self.raw = self.kind.instance()
        self(value=value)

    @property
    def value(self) -> T:
        """Obtain the underlying value."""
        return self.raw.value  # type: ignore

    @value.setter
    def value(self, value: T) -> None:
        """Obtain the underlying value."""
        self.raw.value = value

    def __call__(self, value: T = None) -> T:
        """
        A callable interface for setting and getting the underlying value.
        """
        if value is not None:
            self.value = value
        return self.value

    def __str__(self) -> str:
        """Get this primitive's value as a string."""
        return f"{self.value} ({self.kind})"

    def __eq__(self, other) -> bool:
        """
        Determine if this instance is equivalent to the provided argument.
        """

        if isinstance(other, Primitive):
            other = other.raw.value

        if self.kind.is_float:
            return _isclose(self.raw.value, other)

        return bool(self.raw.value == other)

    def __bool__(self) -> bool:
        """Use the underlying value for boolean evaluation."""
        return bool(self.raw)

    def __bytes__(self) -> bytes:
        """Convert this instance to a byte array."""

        with _BytesIO() as stream:
            self.to_stream(stream)
            return stream.getvalue()

    def to_stream(self, stream: _BinaryIO, byte_order: str = None) -> int:
        """Write this primitive to a stream."""

        if byte_order is None:
            byte_order = self.byte_order

        stream.write(_pack(byte_order + self.kind.format, self.value))
        return self.kind.size

    def from_stream(self, stream: _BinaryIO, byte_order: str = None) -> T:
        """Update this primitive from a stream and return the new value."""

        if byte_order is None:
            byte_order = self.byte_order

        self.value = _unpack(
            byte_order + self.kind.format, stream.read(self.kind.size)
        )[0]
        return self.value
