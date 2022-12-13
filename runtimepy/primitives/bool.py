"""
A module implementing a boolean-primitive interface.
"""

# internal
from runtimepy.primitives.base import Primitive as _Primitive
from runtimepy.primitives.type.bool import Bool as _Bool


class BooleanPrimitive(_Primitive[bool]):
    """A simple primitive class for booleans."""

    def __init__(self, *_, value: bool = False) -> None:
        """Initialize this boolean primitive."""
        super().__init__(_Bool, value=value)

    def toggle(self) -> None:
        """Toggle the underlying value."""
        self.raw.value = not self.raw.value

    def set(self) -> None:
        """Coerce the underlying value to true."""
        self.raw.value = True

    def clear(self) -> None:
        """Coerce the underlying value to false."""
        self.raw.value = False


Bool = BooleanPrimitive
