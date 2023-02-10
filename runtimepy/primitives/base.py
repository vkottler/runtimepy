"""
A module implementing a base, primitive-type storage entity.
"""

# built-in
from copy import copy as _copy
from math import isclose as _isclose
from struct import pack as _pack
from struct import unpack as _unpack
from typing import BinaryIO as _BinaryIO
from typing import Callable as _Callable
from typing import Dict as _Dict
from typing import Generic as _Generic
from typing import Tuple as _Tuple
from typing import TypeVar as _TypeVar

# internal
from runtimepy.primitives.byte_order import (
    DEFAULT_BYTE_ORDER as _DEFAULT_BYTE_ORDER,
)
from runtimepy.primitives.byte_order import ByteOrder as _ByteOrder
from runtimepy.primitives.type import PrimitiveTypelike as _PrimitiveTypelike
from runtimepy.primitives.type import normalize as _normalize

T = _TypeVar("T", bool, int, float)

# Current value first, new value next.
PrimitiveChangeCallaback = _Callable[[T, T], None]


class Primitive(_Generic[T]):
    """A simple class for storing and underlying primitive value."""

    # Use network byte-order by default.
    byte_order: _ByteOrder = _DEFAULT_BYTE_ORDER

    def __init__(self, kind: _PrimitiveTypelike, value: T = None) -> None:
        """Initialize this primitive."""

        assert kind is not None
        self.kind = _normalize(kind)
        self.raw = self.kind.instance()
        self.curr_callback: int = 0
        self.callbacks: _Dict[
            int, _Tuple[PrimitiveChangeCallaback[T], bool]
        ] = {}
        self(value=value)

    @property
    def size(self) -> int:
        """Get the size of this primitive."""
        return self.kind.size

    def __copy__(self) -> "Primitive[T]":
        """Make a copy of this primitive."""
        return type(self)(self.kind, value=self.value)

    def copy(self) -> "Primitive[T]":
        """A simple wrapper for copy."""
        return _copy(self)

    def register_callback(
        self, callback: PrimitiveChangeCallaback[T], once: bool = False
    ) -> int:
        """Register a callback and return an identifier for it."""

        callback_id = self.curr_callback
        self.curr_callback += 1
        self.callbacks[callback_id] = callback, once
        return callback_id

    def remove_callback(self, callback_id: int) -> bool:
        """Remove a callback if one is registered with this identifier."""

        result = callback_id in self.callbacks
        if result:
            del self.callbacks[callback_id]
        return result

    @property
    def value(self) -> T:
        """Obtain the underlying value."""
        return self.raw.value  # type: ignore

    @value.setter
    def value(self, value: T) -> None:
        """Obtain the underlying value."""

        curr: T = self.raw.value  # type: ignore

        # Call callbacks if the value has changed.
        if curr != value and self.callbacks:
            to_remove = []
            for ident, (callback, once) in self.callbacks.items():
                callback(curr, value)
                if once:
                    to_remove.append(ident)

            # Remove one-time callbacks.
            for item in to_remove:
                self.remove_callback(item)

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

    def binary(self, byte_order: _ByteOrder = None) -> bytes:
        """Convert this instance to a byte array."""
        if byte_order is None:
            byte_order = self.byte_order
        return _pack(byte_order.fmt + self.kind.format, self.value)

    def __bytes__(self) -> bytes:
        """Convert this instance to a byte array."""
        return self.binary()

    def to_stream(
        self, stream: _BinaryIO, byte_order: _ByteOrder = None
    ) -> int:
        """Write this primitive to a stream."""

        stream.write(self.binary(byte_order=byte_order))
        return self.kind.size

    def update(self, data: bytes, byte_order: _ByteOrder = None) -> T:
        """Update this primitive from a bytes object."""

        if byte_order is None:
            byte_order = self.byte_order

        self.value = _unpack(byte_order.fmt + self.kind.format, data)[0]
        return self.value

    def from_stream(
        self, stream: _BinaryIO, byte_order: _ByteOrder = None
    ) -> T:
        """Update this primitive from a stream and return the new value."""

        return self.update(stream.read(self.kind.size), byte_order=byte_order)
