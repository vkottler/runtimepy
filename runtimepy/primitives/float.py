"""
A module implementing a floating-point primitive interface.
"""

# internal
from runtimepy.primitives.base import Primitive as _Primitive
from runtimepy.primitives.type.float import Double as _Double
from runtimepy.primitives.type.float import Float as _Float
from runtimepy.primitives.type.float import Half as _Half


class HalfPrimitive(_Primitive[float]):
    """A simple primitive class for single-precision floating-point."""

    def __init__(self, *_, value: float = 0.0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(_Half, value=value)


Half = HalfPrimitive


class FloatPrimitive(_Primitive[float]):
    """A simple primitive class for single-precision floating-point."""

    def __init__(self, *_, value: float = 0.0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(_Float, value=value)


Float = FloatPrimitive


class DoublePrimitive(_Primitive[float]):
    """A simple primitive class for double-precision floating-point."""

    def __init__(self, *_, value: float = 0.0) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(_Double, value=value)


Double = DoublePrimitive
