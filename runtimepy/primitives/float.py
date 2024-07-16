"""
A module implementing a floating-point primitive interface.
"""

# built-in
import math

# internal
from runtimepy.primitives.evaluation import (
    EvalResult,
    Operator,
    PrimitiveIsCloseMixin,
    compare_latest,
)
from runtimepy.primitives.scaling import ChannelScaling, invert
from runtimepy.primitives.types.float import Double as _Double
from runtimepy.primitives.types.float import Float as _Float
from runtimepy.primitives.types.float import Half as _Half


class BaseFloatPrimitive(PrimitiveIsCloseMixin[float]):
    """A simple primitive class for floating-point numbers."""

    def __init__(
        self, value: float = 0.0, scaling: ChannelScaling = None, **kwargs
    ) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(value=value, scaling=scaling, **kwargs)

    def _check_callbacks(self, curr: float, new: float) -> None:
        """Determine if any callbacks should be serviced."""

        # Useless to provide NaN to callbacks.
        if not math.isnan(new):
            super()._check_callbacks(curr, new)

    async def wait_for_value(
        self,
        value: float,
        timeout: float,
        operation: Operator = Operator.EQUAL,
    ) -> EvalResult:
        """Wait for this primitive to reach a specified state."""

        if self.scaling:
            value = invert(value, scaling=self.scaling)

        return await compare_latest(self, value, timeout, operation=operation)


class HalfPrimitive(BaseFloatPrimitive):
    """A simple primitive class for half-precision floating-point."""

    kind = _Half


Half = HalfPrimitive


class FloatPrimitive(BaseFloatPrimitive):
    """A simple primitive class for single-precision floating-point."""

    kind = _Float


Float = FloatPrimitive


class DoublePrimitive(BaseFloatPrimitive):
    """A simple primitive class for double-precision floating-point."""

    kind = _Double


Double = DoublePrimitive
