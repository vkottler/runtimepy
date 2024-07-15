"""
A module implementing a boolean-primitive interface.
"""

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

    def toggle(self) -> None:
        """Toggle the underlying value."""
        self.value = not self.raw.value

    def set(self) -> None:
        """Coerce the underlying value to true."""
        self.value = True

    def clear(self) -> None:
        """Coerce the underlying value to false."""
        self.value = False

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
