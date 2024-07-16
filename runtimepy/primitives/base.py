"""
A module implementing a base, primitive-type storage entity.
"""

# built-in
from contextlib import contextmanager as _contextmanager
from copy import copy as _copy
from math import isclose as _isclose
from typing import BinaryIO as _BinaryIO
from typing import Callable as _Callable
from typing import Generic as _Generic
from typing import Iterator as _Iterator
from typing import TypeVar as _TypeVar

# third-party
from vcorelib.math import default_time_ns, nano_str
from vcorelib.math.keeper import TimeSource

# internal
from runtimepy.primitives.byte_order import (
    DEFAULT_BYTE_ORDER as _DEFAULT_BYTE_ORDER,
)
from runtimepy.primitives.byte_order import ByteOrder as _ByteOrder
from runtimepy.primitives.scaling import ChannelScaling, Numeric, apply, invert
from runtimepy.primitives.types import AnyPrimitiveType as _AnyPrimitiveType
from runtimepy.primitives.types.base import PythonPrimitive as _PythonPrimitive
from runtimepy.util import Identifier

T = _TypeVar("T", bool, int, float)

# Current value first, new value next.
PrimitiveChangeCallaback = _Callable[[T, T], None]

IDENT = Identifier()
IDENT.curr_id = 0
IDENT.scale = 1


class Primitive(_Generic[T]):
    """A simple class for storing an underlying primitive value."""

    # Use network byte-order by default.
    byte_order: _ByteOrder = _DEFAULT_BYTE_ORDER

    # Nominally set the primitive type at the class level.
    kind: _AnyPrimitiveType

    def __hash__(self) -> int:
        """A hash for this instance."""
        return self._hash

    def __init__(
        self,
        value: T = None,
        scaling: ChannelScaling = None,
        time_source: TimeSource = default_time_ns,
    ) -> None:
        """Initialize this primitive."""

        self.raw = self.kind.instance()
        self.curr_callback: int = 0
        self.callbacks: dict[int, tuple[PrimitiveChangeCallaback[T], bool]] = (
            {}
        )
        self.time_source = time_source
        self(value=value)
        self.last_updated_ns: int = self.time_source()
        self.scaling = scaling
        self._hash = IDENT()

    @classmethod
    def valid_primitive(cls, primitive: _PythonPrimitive) -> bool:
        """Determine if a Python primitive is valid for this class."""
        return cls.kind.valid_primitive(primitive)

    def age_ns(self, now: int = None) -> int:
        """Get the age of this primitive's value in nanoseconds."""

        if now is None:
            now = self.time_source()

        return now - self.last_updated_ns

    def age_str(self, now: int = None) -> str:
        """Get the age of this primitive's value as a string."""

        return nano_str(self.age_ns(now=now))

    @property
    def size(self) -> int:
        """Get the size of this primitive."""
        return self.kind.size

    def __copy__(self) -> "Primitive[T]":
        """Make a copy of this primitive."""
        return type(self)(value=self.value)

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

    @_contextmanager
    def callback(
        self, callback: PrimitiveChangeCallaback[T]
    ) -> _Iterator[None]:
        """Register a callback as a managed context."""

        ident = self.register_callback(callback)
        try:
            yield
        finally:
            self.remove_callback(ident)

    @property
    def value(self) -> T:
        """Obtain the underlying value."""
        return self.raw.value  # type: ignore

    @value.setter
    def value(self, value: T) -> None:
        """Set a new underlying value."""
        self.set_value(value)

    def _check_callbacks(self, curr: T, new: T) -> None:
        """Determine if any callbacks should be serviced."""

        if self.callbacks and curr != new:
            to_remove = []
            for ident, (callback, once) in self.callbacks.items():
                callback(curr, new)
                if once:
                    to_remove.append(ident)

            # Remove one-time callbacks.
            for item in to_remove:
                self.remove_callback(item)

    def set_value(self, value: T, timestamp_ns: int = None) -> None:
        """Set a new underlying value."""

        # Set new timestamp.
        if timestamp_ns is None:
            timestamp_ns = self.time_source()
        self.last_updated_ns = timestamp_ns

        curr: T = self.raw.value  # type: ignore
        self.raw.value = value
        self._check_callbacks(curr, value)

    @property
    def scaled(self) -> Numeric:
        """Get this primitive as a scaled value."""
        return self.scale(self.value)

    @scaled.setter
    def scaled(self, value: T) -> None:
        """Set this value but invert scaling information."""
        self.value = self.invert(value)  # type: ignore

    def scale(self, value: T) -> Numeric:
        """Scale a value using this primitive's scaling."""
        return apply(value, scaling=self.scaling)

    def invert(self, value: T) -> Numeric:
        """Invert a value using this primitive's scaling."""

        val = invert(
            value, scaling=self.scaling, should_round=self.kind.is_integer
        )

        if self.kind.int_bounds is not None:
            val = self.kind.int_bounds.clamp(val)  # type: ignore

        return val

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
        return self.kind.encode(self.value, byte_order=byte_order)

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

        self.value = self.kind.decode(  # type: ignore
            data, byte_order=byte_order
        )
        return self.value

    def from_stream(
        self, stream: _BinaryIO, byte_order: _ByteOrder = None
    ) -> T:
        """Update this primitive from a stream and return the new value."""

        return self.update(stream.read(self.kind.size), byte_order=byte_order)

    @classmethod
    def encode(cls, value: T, byte_order: _ByteOrder = None) -> bytes:
        """Create a bytes instance based on this primitive type."""
        if byte_order is None:
            byte_order = cls.byte_order
        return cls.kind.encode(value, byte_order=byte_order)

    @classmethod
    def decode(cls, data: bytes, byte_order: _ByteOrder = None) -> T:
        """Decode a primitive of this type from provided data."""

        if byte_order is None:
            byte_order = cls.byte_order

        return cls.kind.decode(data, byte_order=byte_order)  # type: ignore

    @classmethod
    def read(cls, stream: _BinaryIO, byte_order: _ByteOrder = None) -> T:
        """
        Read a primitive from the provided stream based on this primitive type.
        """

        if byte_order is None:
            byte_order = cls.byte_order

        return cls.kind.read(stream, byte_order=byte_order)  # type: ignore

    @classmethod
    def write(
        cls, value: T, stream: _BinaryIO, byte_order: _ByteOrder = None
    ) -> int:
        """Write a primitive to the stream based on this type."""

        if byte_order is None:
            byte_order = cls.byte_order

        return cls.kind.write(value, stream, byte_order=byte_order)
