"""
A module for implementing a base class for primitive types.
"""

# built-in
import ctypes as _ctypes
from struct import calcsize as _calcsize
from typing import Generic as _Generic
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import cast as _cast

# Integer type aliases.
Int8Ctype = _ctypes.c_byte
Int16Ctype = _ctypes.c_short
Int32Ctype = _ctypes.c_int
Int64Ctype = _ctypes.c_longlong
Uint8Ctype = _ctypes.c_ubyte
Uint16Ctype = _ctypes.c_ushort
Uint32Ctype = _ctypes.c_uint
Uint64Ctype = _ctypes.c_ulonglong

# Floating-point type aliases.
FloatCtype = _ctypes.c_float
DoubleCtype = _ctypes.c_double

# Boolean type alias.
BoolCtype = _ctypes.c_bool

# This variable declaration doesn't seem to work well using unions of types
# (e.g. if "signed integers" and "unsigned integers" were unions of respective
# ctypes, and this was a union of those).
T = _TypeVar(
    "T",
    # Integer types.
    Int8Ctype,
    Int16Ctype,
    Int32Ctype,
    Int64Ctype,
    Uint8Ctype,
    Uint16Ctype,
    Uint32Ctype,
    Uint64Ctype,
    # Floating-point types.
    FloatCtype,
    DoubleCtype,
    # Boolean type.
    BoolCtype,
)


class PrimitiveType(_Generic[T]):
    """A simple wrapper around ctype primitives."""

    # Sub-classes must set these class attributes.
    name: str
    c_type: _Type[T]

    def __init__(self, struct_format: str) -> None:
        """Initialize this primitive type."""

        self.format = struct_format

        # Make sure that the struct size and ctype size match. There's
        # unfortunately no obvious (or via public interfaces) way to just
        # obtain the intended struct formatter for each ctype.
        self.size = _calcsize(self.format)
        self.bits = self.size * 8
        c_type_size = _ctypes.sizeof(self.c_type)

        # This won't match for half-precision floating-point.
        if self.format != "e":
            assert self.size == c_type_size, "{self.size} != {c_type_size}!"

        # Convenient attributes to determine if this type is which one of
        # Python's primitive types.
        self.is_boolean = self.c_type == _ctypes.c_bool
        self.is_float = any(
            self.c_type == x for x in [_ctypes.c_float, _ctypes.c_double]
        )
        self.is_integer = (not self.is_boolean) and (not self.is_float)

    def __str__(self) -> str:
        """Get this type as a string."""
        return self.name

    def __hash__(self) -> int:
        """Get a hash for this type."""
        return hash(self.c_type)

    def __eq__(self, other) -> bool:
        """Determine if two types are equal."""
        if isinstance(other, PrimitiveType):
            other = other.c_type
        return _cast(bool, self.c_type == other)

    @classmethod
    def instance(cls) -> T:
        """Get an instance of this primitive type."""
        return cls.c_type()
