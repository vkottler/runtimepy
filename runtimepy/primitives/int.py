"""
A module implementing an integer-primitive interface.
"""

# built-in
from typing import Union as _Union

# internal
from runtimepy.primitives.base import Primitive as _Primitive
from runtimepy.primitives.type.int import Int8 as _Int8
from runtimepy.primitives.type.int import Int16 as _Int16
from runtimepy.primitives.type.int import Int32 as _Int32
from runtimepy.primitives.type.int import Int64 as _Int64
from runtimepy.primitives.type.int import Uint8 as _Uint8
from runtimepy.primitives.type.int import Uint16 as _Uint16
from runtimepy.primitives.type.int import Uint32 as _Uint32
from runtimepy.primitives.type.int import Uint64 as _Uint64


class Int8Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    def __init__(self, *_, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(_Int8, value=value)


Int8 = Int8Primitive


class Int16Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    def __init__(self, *_, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(_Int16, value=value)


Int16 = Int16Primitive


class Int32Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    def __init__(self, *_, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(_Int32, value=value)


Int32 = Int32Primitive


class Int64Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    def __init__(self, *_, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(_Int64, value=value)


Int64 = Int64Primitive


class Uint8Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    def __init__(self, *_, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(_Uint8, value=value)


Uint8 = Uint8Primitive


class Uint16Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    def __init__(self, *_, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(_Uint16, value=value)


Uint16 = Uint16Primitive


class Uint32Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    def __init__(self, *_, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(_Uint32, value=value)


Uint32 = Uint32Primitive


class Uint64Primitive(_Primitive[int]):
    """A simple primitive class for single-precision floating-point."""

    def __init__(self, *_, value: int = 0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(_Uint64, value=value)


Uint64 = Uint64Primitive
UnsignedInt = _Union[Uint8, Uint16, Uint32, Uint64]
