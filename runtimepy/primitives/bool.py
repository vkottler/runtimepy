"""
A module implementing a boolean-primitive interface.
"""

# built-in
from random import getrandbits

# internal
from runtimepy.primitives.base import Primitive as _Primitive
from runtimepy.primitives.evaluation import EvalResult, evaluate
from runtimepy.primitives.types.bool import Bool as _Bool


class BooleanPrimitive(_Primitive[bool]):
    """A simple primitive class for booleans."""

    kind = _Bool
    value: bool

    def __init__(self, value: bool = False, **kwargs) -> None:
        """Initialize this boolean primitive."""
        super().__init__(value=value, **kwargs)

    def randomize(self, timestamp_ns: int = None) -> None:
        """Set this primitive to a random integer."""
        self.set_value(bool(getrandbits(1)), timestamp_ns=timestamp_ns)

    def toggle(self, timestamp_ns: int = None) -> None:
        """Toggle the underlying value."""
        self.set_value(not self.raw.value, timestamp_ns=timestamp_ns)

    def set(self, timestamp_ns: int = None) -> None:
        """Coerce the underlying value to true."""
        self.set_value(True, timestamp_ns=timestamp_ns)

    def clear(self, timestamp_ns: int = None) -> None:
        """Coerce the underlying value to false."""
        self.set_value(False, timestamp_ns=timestamp_ns)

    async def wait_for_state(self, state: bool, timeout: float) -> EvalResult:
        """Wait for this primitive to reach a specified state."""

        return await evaluate(
            self,
            lambda _, new: (
                EvalResult.SUCCESS if new == state else EvalResult.FAIL
            ),
            timeout,
        )


Bool = BooleanPrimitive
