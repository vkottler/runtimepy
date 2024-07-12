"""
A module implementing interfaces for evaluating the underlying state of
primitives.
"""

# built-in
import asyncio
from enum import auto
from typing import Callable

# internal
from runtimepy.enum.registry import RuntimeIntEnum
from runtimepy.primitives.base import Primitive, T


class EvalResult(RuntimeIntEnum):
    """A container for all possible evaluation results."""

    NOT_SET = auto()

    TIMEOUT = auto()
    FAIL = auto()
    SUCCESS = auto()

    def __bool__(self) -> bool:
        """Determine success status of this instance."""
        return self is EvalResult.SUCCESS


PrimitiveEvaluator = Callable[[T, T], EvalResult]


async def evaluate(
    primitive: Primitive[T], evaluator: PrimitiveEvaluator[T], timeout: float
) -> EvalResult:
    """
    Evaluate a primitive within a timeout constraint and return the result.
    """

    # Short-circuit path.
    if evaluator(primitive.value, primitive.value):
        return EvalResult.SUCCESS

    event = asyncio.Event()
    result = EvalResult.TIMEOUT

    def change_callback(curr: T, new: T) -> None:
        """Handle underlying value changes to the provided primitive."""

        # Always update the result when called.
        nonlocal result
        result = evaluator(curr, new)
        if result:
            event.set()

    # Service the callback until resolved or this evaluation times out.
    with primitive.callback(change_callback):
        try:
            await asyncio.wait_for(event.wait(), timeout)
        except asyncio.TimeoutError:
            pass

    return result
