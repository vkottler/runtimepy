"""
A bit-field manager.
"""

# built-in
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import cast as _cast

# internal
from runtimepy.primitives import Primitivelike as _Primitivelike
from runtimepy.primitives import normalize as _normalize
from runtimepy.primitives.field import BitField as _BitField
from runtimepy.primitives.field import BitFlag as _BitFlag
from runtimepy.primitives.int import UnsignedInt as _UnsignedInt

T = _TypeVar("T", bound="BitFieldManager")


class BitFieldManager:
    """
    A class for managing multiple bit-fields belonging to a single, primitive
    integer.
    """

    def __init__(self, raw: _UnsignedInt) -> None:
        """Initialize this bit-field manager."""

        self.raw = raw
        self.curr_index = 0
        self.bits_available = set(range(self.raw.kind.bits))

    def flag(self, index: int = None) -> _BitFlag:
        """Create a new bit flag."""

        idx = index if index is not None else self.curr_index

        assert (
            idx in self.bits_available
        ), f"Bit at index {idx} is already allocated!"

        self.bits_available.remove(idx)

        # Advance the current index if it was used for this flag.
        if index is None:
            self.curr_index += 1

        return _BitFlag(self.raw, idx)

    def field(self, width: int, index: int = None) -> _BitField:
        """Create a new bit field."""

        assert width != 1, "Use bit-flags for single-width fields!"

        idx = index if index is not None else self.curr_index

        # Ensure that all bits for this field are available.
        bits = set(x + idx for x in range(width))
        for bit in bits:
            assert (
                bit in self.bits_available
            ), f"Bit {bit} is already allocated!"

        # Allocate bits.
        self.bits_available -= bits

        # Advance the current index if it was used for this field.
        if index is None:
            self.curr_index += width

        return _BitField(self.raw, idx, width)

    @classmethod
    def create(cls: _Type[T], value: _Primitivelike = "uint8") -> T:
        """Create a new bit-field manager."""

        return cls(_cast(_UnsignedInt, _normalize(value)()))
