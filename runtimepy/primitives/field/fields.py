"""
A module implementing a data structure for managing multiple bit fields.
"""

# built-in
from typing import Iterator as _Iterator
from typing import Optional as _Optional
from typing import TypeVar as _TypeVar
from typing import Union as _Union
from typing import cast as _cast

# third-party
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.io.types import JsonValue as _JsonValue

# internal
from runtimepy.primitives import Primitivelike as _Primitivelike
from runtimepy.primitives import normalize as _normalize
from runtimepy.primitives.field import BitField as _BitField
from runtimepy.primitives.field import BitFieldBase as _BitFieldBase
from runtimepy.primitives.field import BitFlag as _BitFlag
from runtimepy.primitives.int import UnsignedInt as _UnsignedInt
from runtimepy.registry.name import RegistryKey as _RegistryKey
from runtimepy.schemas import RuntimepyDictCodec as _RuntimepyDictCodec

T = _TypeVar("T", bound="BitFields")


class BitFields(_RuntimepyDictCodec):
    """A class for managing bit fields and flags from dictionary data."""

    curr_index: int
    _finalized: bool

    def init(self, data: _JsonObject) -> None:
        """Perform implementation-specific initialization."""

        # Create the underlying storage element.
        self.raw: _UnsignedInt = _cast(
            _UnsignedInt, _normalize(_cast(str, data["type"]))()
        )

        self.curr_index = 0
        self.bits_available = set(range(self.raw.kind.bits))
        self.fields: dict[str, _BitField] = {}
        self.by_index: dict[int, _Union[_BitField, tuple[int, int]]] = {}

        # Set this initially false while we're initializing.
        self._finalized: bool = False

        # Load initial fields and flags.
        for item in _cast(list[dict[str, int]], data["fields"]):
            name: str = _cast(str, item.get("name", ""))
            index: _Optional[int] = item.get("index")
            width: int = item["width"]
            value: int = int(item["value"])
            commandable: bool = bool(item.get("commandable", False))
            enum = item.get("enum")
            desc: _Optional[str] = _cast(str, item.get("description"))

            # Fields without names are considered padding.
            if not name:
                assert value == 0, "Can't set padding to non-zero value!"
                assert enum is None, f"Enum '{enum}' specified for padding!"
                item["index"] = self.pad(width=width, index=index)
                continue

            if width == 1:
                flag = self.flag(
                    name,
                    index=index,
                    enum=enum,
                    description=desc,
                    commandable=commandable,
                )
                flag(value)
                item["index"] = flag.index
            else:
                field = self.field(
                    name,
                    width,
                    index=index,
                    enum=enum,
                    description=desc,
                    commandable=commandable,
                )
                field(value)
                item["index"] = field.index

        self._finalized: bool = _cast(bool, data["finalized"])

    @property
    def names(self) -> _Iterator[str]:
        """Iterate over names mapping to individual fields."""
        yield from self.fields

    def finalize(self) -> None:
        """Finalize the fields so that new fields can't be added."""
        self._finalized = True

    def asdict(self) -> _JsonObject:
        """Get these bit fields as a dictionary."""

        fields: list[dict[str, _Union[str, int]]] = []

        # Ensure both real fields and padding are encoded.
        for index, item in self.by_index.items():
            if isinstance(item, tuple):
                fields.append(
                    {"index": index, "width": item[0], "value": item[1]}
                )
            else:
                fields.append(item.asdict())  # type: ignore

        return {
            "type": str(self.raw.kind),
            "fields": _cast(_JsonValue, fields),
            "finalized": self._finalized,
        }

    def get_field(self, key: _RegistryKey) -> _Optional[_BitField]:
        """Attempt to get a bit-field from this entity."""

        if isinstance(key, str):
            return self.fields.get(key)

        result = self.by_index.get(key)
        assert not isinstance(result, tuple), f"Field at '{key}' is padding!"
        return result

    def __getitem__(self, key: _RegistryKey) -> _BitField:
        """Obtain a bit-field."""

        result = self.get_field(key)
        if result is None:
            raise KeyError(f"No field '{key}'!")
        return result

    def flag(
        self,
        name: str,
        index: int = None,
        enum: _RegistryKey = None,
        description: str = None,
        **kwargs,
    ) -> _BitFlag:
        """Create a new bit flag."""

        index = self._claim_bits(1, index=index)

        result = _BitFlag(
            name, self.raw, index, enum=enum, description=description, **kwargs
        )

        self.fields[name] = result
        self.by_index[index] = result
        return result

    def _claim_bits(self, width: int, index: int = None) -> int:
        """Allocate bits within this primitive."""

        assert not self._finalized, "Can't add any more bits!"

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

        # Advance the current index if this index is the same or larger.
        if index >= self.curr_index:
            self.curr_index = index + width

        return index

    def pad(self, width: int = 1, index: int = None, val: int = 0) -> int:
        """Pad bits in this primitive so they can't be allocated."""

        result = self._claim_bits(width, index=index)

        # Ensure the padded field is still set to the correct value.
        _BitFieldBase(self.raw, result, width)(val=val)

        self.by_index[result] = (width, val)
        return result

    def claim_field(self, field: _BitField) -> _BitField:
        """Claim a bit field."""

        assert field.name not in self.fields, field.name
        self.fields[field.name] = field
        self.by_index[field.index] = field
        return field

    def field(
        self,
        name: str,
        width: int,
        index: int = None,
        enum: _RegistryKey = None,
        description: str = None,
        **kwargs,
    ) -> _BitField:
        """Create a new bit field."""

        assert width != 1, "Use bit-flags for single-width fields!"

        return self.claim_field(
            _BitField(
                name,
                self.raw,
                self._claim_bits(width, index=index),
                width,
                enum=enum,
                description=description,
                **kwargs,
            )
        )

    @classmethod
    def new(cls: type[T], value: _Primitivelike = "uint8") -> T:
        """Create a new bit-field storage entity."""

        return cls.create(
            {"type": _cast(str, value), "fields": [], "finalized": False}
        )
