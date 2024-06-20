"""
A module implementing a floating-point primitive interface.
"""

# internal
from runtimepy.primitives.base import Primitive as _Primitive
from runtimepy.primitives.scaling import ChannelScaling
from runtimepy.primitives.types.float import Double as _Double
from runtimepy.primitives.types.float import Float as _Float
from runtimepy.primitives.types.float import Half as _Half


class HalfPrimitive(_Primitive[float]):
    """A simple primitive class for single-precision floating-point."""

    kind = _Half

    def __init__(
        self, value: float = 0.0, scaling: ChannelScaling = None, **kwargs
    ) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(value=value, scaling=scaling, **kwargs)


Half = HalfPrimitive


class FloatPrimitive(_Primitive[float]):
    """A simple primitive class for single-precision floating-point."""

    kind = _Float

    def __init__(
        self, value: float = 0.0, scaling: ChannelScaling = None, **kwargs
    ) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(value=value, scaling=scaling, **kwargs)


Float = FloatPrimitive


class DoublePrimitive(_Primitive[float]):
    """A simple primitive class for double-precision floating-point."""

    kind = _Double

    def __init__(
        self, value: float = 0.0, scaling: ChannelScaling = None, **kwargs
    ) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(value=value, scaling=scaling, **kwargs)


Double = DoublePrimitive
