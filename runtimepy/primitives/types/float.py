"""
A module implementing a type interface for floating-point numbers.
"""

# internal
from runtimepy.primitives.types.base import DoubleCtype as _DoubleCtype
from runtimepy.primitives.types.base import FloatCtype as _FloatCtype
from runtimepy.primitives.types.base import PrimitiveType as _PrimitiveType


class HalfType(_PrimitiveType[_FloatCtype]):
    """A simple type interface for single-precision floating-point."""

    name = "half"

    # There's no half-precision floating-point ctypes equivalent.
    c_type = _FloatCtype
    python_type = float

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__("e")
        assert self.is_float


Half = HalfType()


class FloatType(_PrimitiveType[_FloatCtype]):
    """A simple type interface for single-precision floating-point."""

    name = "float"
    c_type = _FloatCtype
    python_type = float

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__("f")
        assert self.is_float


Float = FloatType()


class DoubleType(_PrimitiveType[_DoubleCtype]):
    """A simple type interface for double-precision floating-point."""

    name = "double"
    c_type = _DoubleCtype
    python_type = float

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__("d")
        assert self.is_float


Double = DoubleType()
