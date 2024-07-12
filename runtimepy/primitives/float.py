"""
A module implementing a floating-point primitive interface.
"""

# built-in
from math import isclose

# internal
from runtimepy.primitives.base import Primitive as _Primitive
from runtimepy.primitives.evaluation import (
    EvalResult,
    Operator,
    compare_latest,
    evaluate,
)
from runtimepy.primitives.scaling import ChannelScaling, invert
from runtimepy.primitives.types.float import Double as _Double
from runtimepy.primitives.types.float import Float as _Float
from runtimepy.primitives.types.float import Half as _Half


class BaseFloatPrimitive(_Primitive[float]):
    """A simple primitive class for floating-point numbers."""

    def __init__(
        self, value: float = 0.0, scaling: ChannelScaling = None, **kwargs
    ) -> None:
        """Initialize this floating-point primitive."""
        super().__init__(value=value, scaling=scaling, **kwargs)

    async def wait_for_value(
        self,
        value: float,
        timeout: float,
        operation: Operator = Operator.EQUAL,
    ) -> EvalResult:
        """Wait for this primitive to reach a specified state."""

        # Invert a possible scaling as primitive evaluation does not apply it.
        # This skips a per-update computation, though scaling 'new' in the
        # evaluator would allow this to work for more complex scalars.
        if self.scaling:
            value = invert(
                value,
                scaling=self.scaling,
                should_round=True,
            )

        return await compare_latest(self, value, timeout, operation=operation)

    async def wait_for_isclose(
        self,
        value: float,
        timeout: float,
        rel_tol: float = 1e-09,
        abs_tol: float = 0.0,
    ) -> EvalResult:
        """Wait for this primitive to reach a specified state."""

        # See note in 'BaseIntPrimitive.wait_for_value'.
        value = invert(value, scaling=self.scaling)

        return await evaluate(
            self,
            lambda _, new: (
                EvalResult.SUCCESS
                if isclose(value, new, rel_tol=rel_tol, abs_tol=abs_tol)
                else EvalResult.FAIL
            ),
            timeout,
        )


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
