"""
A module implementing bit flags and fields.
"""

# built-in
from typing import cast as _cast

# internal
from runtimepy.primitives.int import UnsignedInt as _UnsignedInt


class BitField:
    """A class managing a portion of an unsigned-integer primitive."""

    def __init__(self, raw: _UnsignedInt, index: int, width: int) -> None:
        """Initialize this bit-field."""

        # Verify bit-field parameters.
        assert (
            raw.kind.is_integer
        ), f"Can't create a bit field with {raw.kind}!"
        assert (
            index < raw.kind.bits
        ), f"Field can't start at {index} for {raw.kind}!"
        assert (
            width <= raw.kind.bits
        ), f"Field can't be {width}-bits wide for {raw.kind}!"

        self.raw = raw
        self.index = index

        # Compute a bit-mask for this field.
        self.mask = (2**width) - 1
        self.shifted_mask = self.mask << self.index

    def __call__(self, val: int = None) -> int:
        """
        Set (or get) the underlying value of this field. Return the actual
        value of the field.
        """

        # Apply the field mask.
        result: int
        if val is not None:
            result = val & self.mask

            # Get the underlying value and apply the new value.
            self.raw.value = (self.raw.value & ~self.shifted_mask) | (
                result << self.index
            )
        else:
            result = _cast(
                int, (self.raw.value & self.shifted_mask) >> self.index
            )

        return result


class BitFlag(BitField):
    """A bit field that is always a single bit."""

    def __init__(self, raw: _UnsignedInt, index: int) -> None:
        """Initialize this bit flag."""
        super().__init__(raw, index, 1)

    def clear(self) -> None:
        """Clear this field."""
        self(val=0)

    def set(self, val: bool = True) -> None:
        """Set this flag."""
        self(val=int(val))

    def get(self) -> bool:
        """Get the value of this flag."""
        return bool(self())
