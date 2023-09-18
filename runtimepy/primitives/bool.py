"""
A module implementing a boolean-primitive interface.
"""

# built-in
from typing import NamedTuple

# internal
from runtimepy.primitives.base import Primitive as _Primitive
from runtimepy.primitives.type.bool import Bool as _Bool


class BooleanPrimitive(_Primitive[bool]):
    """A simple primitive class for booleans."""

    kind = _Bool

    def __init__(self, value: bool = False) -> None:
        """Initialize this boolean primitive."""
        super().__init__(value=value)

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


class StrToBool(NamedTuple):
    """A container for results when converting strings to boolean."""

    result: bool
    valid: bool

    @staticmethod
    def parse(data: str) -> "StrToBool":
        """Parse a string to boolean."""

        data = data.lower()
        is_true = data == "true"
        resolved = is_true or data == "false"
        return StrToBool(is_true, resolved)
