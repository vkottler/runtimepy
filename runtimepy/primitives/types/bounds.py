"""
A module implementing an interface for keeping track of primitive-integer
bounds (based on bit width).
"""

# built-in
from random import randint
from typing import NamedTuple


class IntegerBounds(NamedTuple):
    """A container for integer bounds."""

    min: int
    max: int

    def random(self) -> int:
        """Get a random integer."""
        return randint(self.min, self.max)

    def validate(self, val: int) -> bool:
        """Determine if the value is within bounds."""
        return self.min <= val <= self.max

    def clamp(self, val: int) -> int:
        """
        Ensure that 'val' is between min and max, use the min or max value
        instead of the provided value if it exceeds these bounds.
        """

        return max(self.min, min(val, self.max))

    @staticmethod
    def create(byte_count: int, signed: bool) -> "IntegerBounds":
        """Compute maximum and minimum values given size and signedness."""

        min_val = 0 if not signed else -1 * (2 ** (byte_count * 8 - 1))
        width = 8 * byte_count if not signed else 8 * byte_count - 1
        return IntegerBounds(min_val, (2**width) - 1)
