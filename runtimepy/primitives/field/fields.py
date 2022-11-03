"""
A module implementing a data structure for managing multiple bit fields.
"""

# built-in
from typing import Dict as _Dict
from typing import List as _List
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import cast as _cast

# third-party
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.io.types import JsonValue as _JsonValue

# internal
from runtimepy.primitives import Primitivelike as _Primitivelike
from runtimepy.primitives import normalize as _normalize
from runtimepy.primitives.field import BitField as _BitField
from runtimepy.primitives.field import BitFlag as _BitFlag
from runtimepy.primitives.int import UnsignedInt as _UnsignedInt
from runtimepy.schemas import RuntimepyDictCodec as _RuntimepyDictCodec

T = _TypeVar("T", bound="BitFields")


class BitFields(_RuntimepyDictCodec):
    """A class for managing bit fields and flags from dictionary data."""

    curr_index: int

    def init(self, data: _JsonObject) -> None:
        """Perform implementation-specific initialization."""

        # Create the underlying storage element.
        self.raw: _UnsignedInt = _cast(
            _UnsignedInt, _normalize(_cast(str, data["type"]))()
        )

        self.curr_index = 0
        self.bits_available = set(range(self.raw.kind.bits))
        self.flags: _Dict[int, _BitFlag] = {}
        self.fields: _Dict[int, _BitField] = {}

        # Load initial fields and flags.
        for item in _cast(_List[_Dict[str, int]], data["fields"]):
            index: int = item["index"]
            width: int = item["width"]
            value: int = item["value"]

            if width == 1:
                self.flag(index=index)(value)
            else:
                self.field(width, index=index)(value)

    def asdict(self) -> _JsonObject:
        """Get these bit fields as a dictionary."""

        return {
            "type": str(self.raw.kind),
            "fields": _cast(
                _JsonValue,
                [x.asdict() for x in self.flags.values()]
                + [x.asdict() for x in self.fields.values()],
            ),
        }

    def flag(self, index: int = None) -> _BitFlag:
        """Create a new bit flag."""

        if index is None:
            index = self.curr_index

        assert (
            index in self.bits_available
        ), f"Bit at index {index} is already allocated!"

        self.bits_available.remove(index)

        result = _BitFlag(self.raw, index)

        # Advance the current index if this index is the same or larger.
        if index >= self.curr_index:
            self.curr_index = index + 1

        self.flags[index] = result
        return result

    def field(self, width: int, index: int = None) -> _BitField:
        """Create a new bit field."""

        assert width != 1, "Use bit-flags for single-width fields!"

        if index is None:
            index = self.curr_index

        # Ensure that all bits for this field are available.
        bits = set(x + index for x in range(width))
        for bit in bits:
            assert (
                bit in self.bits_available
            ), f"Bit {bit} is already allocated!"

        # Allocate bits.
        self.bits_available -= bits

        result = _BitField(self.raw, index, width)

        # Advance the current index if this index is the same or larger.
        if index >= self.curr_index:
            self.curr_index = index + width

        self.fields[index] = result
        return result

    @classmethod
    def new(cls: _Type[T], value: _Primitivelike = "uint8") -> T:
        """Create a new bit-field storage entity."""

        return cls.create({"type": _cast(str, value), "fields": []})
