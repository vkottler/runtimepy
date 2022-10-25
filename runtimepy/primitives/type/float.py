"""
A module implementing a type interface for floating-point numbers.
"""

# internal
from runtimepy.primitives.type.base import DoubleCtype as _DoubleCtype
from runtimepy.primitives.type.base import FloatCtype as _FloatCtype
from runtimepy.primitives.type.base import PrimitiveType as _PrimitiveType


class FloatType(_PrimitiveType[_FloatCtype]):
    """A simple type interface for single-precision floating-point."""

    name = "float"
    c_type = _FloatCtype

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__("f")
        assert self.is_float


Float = FloatType()


class DoubleType(_PrimitiveType[_DoubleCtype]):
    """A simple type interface for double-precision floating-point."""

    name = "double"
    c_type = _DoubleCtype

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__("d")
        assert self.is_float


Double = DoubleType()
