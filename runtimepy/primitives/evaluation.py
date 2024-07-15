"""
A module implementing interfaces for evaluating the underlying state of
primitives.
"""

# built-in
import asyncio
from enum import auto
from math import isclose
import operator
from typing import AsyncIterator, Callable

# internal
from runtimepy.enum.registry import RuntimeIntEnum
from runtimepy.primitives.base import Primitive, T


class Operator(RuntimeIntEnum):
    """https://docs.python.org/3/library/operator.html."""

    LESS_THAN = auto()
    LESS_THAN_OR_EQUAL = auto()

    EQUAL = auto()
    NOT_EQUAL = auto()

    GREATER_THAN_OR_EQUAL = auto()
    GREATER_THAN = auto()


OPERATOR_MAP = {
    Operator.LESS_THAN: operator.lt,
    Operator.LESS_THAN_OR_EQUAL: operator.le,
    Operator.EQUAL: operator.eq,
    Operator.NOT_EQUAL: operator.ne,
    Operator.GREATER_THAN_OR_EQUAL: operator.ge,
    Operator.GREATER_THAN: operator.gt,
}


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


async def compare_latest(
    primitive: Primitive[T],
    lhs: T,
    timeout: float,
    operation: Operator = Operator.EQUAL,
) -> EvalResult:
    """
    Perform a canonical comparison of the latest value with a provided value.
    """

    mapped = OPERATOR_MAP[operation]

    return await evaluate(
        primitive,
        lambda _, new: (
            EvalResult.SUCCESS if mapped(lhs, new) else EvalResult.FAIL
        ),
        timeout,
    )


async def sample_for(
    primitive: Primitive[T],
    timeout: float,
    count: int = -1,
    current: bool = True,
) -> AsyncIterator[tuple[T, int]]:
    """
    Sample a primitive until timeout or 'count' samples are emitted (if 'count'
    is set).
    """

    sample_queue: asyncio.Queue[tuple[T, int]] = asyncio.Queue()
    keep_sampling = True
    samples = 0

    def poll_sample_event() -> bool:
        """Poll sample count."""

        nonlocal samples
        samples += 1

        result = samples >= count > 0
        if result:
            nonlocal keep_sampling
            keep_sampling = False

        return result

    # Publish current value.
    if current:
        sample_queue.put_nowait((primitive.value, primitive.last_updated_ns))
        poll_sample_event()

    def sample(_: T, new: T) -> None:
        """Publish to change queue."""

        if keep_sampling:
            sample_queue.put_nowait((new, primitive.last_updated_ns))
            poll_sample_event()

    # Service the callback until resolved or this evaluation times out.
    with primitive.callback(sample):
        try:
            async with asyncio.timeout(timeout):
                while keep_sampling:
                    yield await sample_queue.get()
        except asyncio.TimeoutError:
            pass

    # Drain queue.
    while not sample_queue.empty():
        yield sample_queue.get_nowait()


class PrimitiveIsCloseMixin(Primitive[T]):
    """Adds a wait-for-isclose method."""

    async def wait_for_isclose(
        self,
        value: float,
        timeout: float,
        rel_tol: float = 1e-09,
        abs_tol: float = 0.0,
    ) -> EvalResult:
        """Wait for this primitive to reach a specified state."""

        return await evaluate(
            self,
            lambda _, new: (
                EvalResult.SUCCESS
                if isclose(
                    value, self.scale(new), rel_tol=rel_tol, abs_tol=abs_tol
                )
                else EvalResult.FAIL
            ),
            timeout,
        )
