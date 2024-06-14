"""
A base management entity for bit-fields.
"""

# built-in
from copy import copy as _copy
from typing import Iterable as _Iterable
from typing import Optional as _Optional
from typing import TypeVar as _TypeVar
from typing import Union as _Union
from typing import cast as _cast

# third-party
from vcorelib.io import ARBITER as _ARBITER
from vcorelib.io.types import EncodeResult as _EncodeResult
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.paths import Pathlike as _Pathlike

# internal
from runtimepy.enum import RuntimeEnum as _RuntimeEnum
from runtimepy.enum.registry import EnumRegistry as _EnumRegistry
from runtimepy.primitives import AnyPrimitive, StrToBool
from runtimepy.primitives.field import BitField as _BitField
from runtimepy.primitives.field import BitFlag as _BitFlag
from runtimepy.primitives.field.fields import BitFields as _BitFields
from runtimepy.registry.name import NameRegistry as _NameRegistry
from runtimepy.registry.name import RegistryKey as _RegistryKey


def fields_to_dict(fields: _Iterable[_BitFields]) -> _JsonObject:
    """Organize a bit-fields iterable into a JSON object."""
    return {"items": [_cast(str, x.asdict()) for x in fields]}


def fields_to_file(
    path: _Pathlike, fields: _Iterable[_BitFields], **kwargs
) -> _EncodeResult:
    """Write bit-fields to a file."""
    return _ARBITER.encode(path, fields_to_dict(fields), **kwargs)


T = _TypeVar("T", bound="BitFieldsManagerBase")


class BitFieldsManagerBase:
    """A class for managing multiple bit-fields objects."""

    def __init__(
        self,
        registry: _NameRegistry,
        enums: _EnumRegistry,
        fields: _Iterable[_BitFields] = None,
    ) -> None:
        """Initialize this bit-fields manager."""

        # Use a channel registry to register field names to.
        self.registry = registry
        self.enums = enums

        if fields is None:
            fields = []

        self.fields: list[_BitFields] = []
        self.by_primitive: dict[AnyPrimitive, _BitFields] = {}
        self.lookup: dict[str, int] = {}
        self.enum_lookup: dict[str, _RuntimeEnum] = {}

        # Add initial fields.
        for field in fields:
            self.add(field)

    def __copy__(self: T) -> T:
        """
        Create a copy of the manager with fields that use distinct underlying
        primitives.
        """
        return self.__class__(
            self.registry, self.enums, fields=[_copy(x) for x in self.fields]
        )

    def asdict(self) -> _JsonObject:
        """Get this bit-fields manager as a JSON object."""
        return fields_to_dict(self.fields)

    def encode(self, path: _Pathlike, **kwargs) -> _EncodeResult:
        """Encode this bit-fields manager to a file."""
        return fields_to_file(path, self.fields, **kwargs)

    def add(self, fields: _BitFields) -> int:
        """Add new bit-fields to manage."""

        # Ensure that new fields can't be added after the current fields
        # are snapshotted.
        fields.finalize()

        index = len(self.fields)
        self.fields.append(fields)

        # Register fields into the lookup structure.
        for name, field in fields.fields.items():
            ident = self.registry.register_name(name)
            assert ident is not None, "Couldn't register bit-field '{name}'!"
            self.lookup[name] = index

            # Also store the enum mapping.
            if field.is_enum:
                self.enum_lookup[name] = self.enums[field.enum]

        return index

    def set(
        self,
        key: _RegistryKey,
        value: _Union[int, bool, str],
        scaled: bool = True,
    ) -> None:
        """Set a value of a field."""

        # Bit fields don't support scaling.
        del scaled

        field = self[key]

        if isinstance(value, str):
            if field.name in self.enum_lookup:
                value = self.enum_lookup[field.name].get_int(value)
            else:
                parsed = StrToBool.parse(value)
                if parsed.valid:
                    value = parsed.result

        # Update the value.
        field(int(value))

    def get(
        self, key: _RegistryKey, resolve_enum: bool = True, scaled: bool = True
    ) -> _Union[int, bool, str]:
        """Get the value of a field."""

        # Bit fields don't support scaling.
        del scaled

        field = self[key]
        value: _Union[int, str] = field()

        if field.is_enum and resolve_enum:
            name = self.registry.name(key)
            assert name is not None, key
            value = self.enum_lookup[name].get_str(value)

        elif field.width == 1:
            value = bool(value)

        return value

    def values(self, resolve_enum: bool = True) -> dict[str, _Union[str, int]]:
        """Get a new dictionary of current field values."""

        return {
            name: self.get(name, resolve_enum=resolve_enum)
            for name in self.lookup
        }

    def get_fields(self, key: _RegistryKey) -> _Optional[_BitFields]:
        """Attempt to get a bit-fields object from a registry key."""

        result = None
        name = self.registry.name(key)

        if name is not None and name in self.lookup:
            result = self.fields[self.lookup[name]]

        return result

    def get_field(self, key: _RegistryKey) -> _Optional[_BitField]:
        """Attempt to get a bit-field."""

        result = None
        name = self.registry.name(key)

        if name is not None:
            fields = self.get_fields(name)
            if fields is not None:
                result = fields[name]

        return result

    def get_flag(self, key: _RegistryKey) -> _BitFlag:
        """Attempt to lookup a bit-flag."""

        result = self[key]
        if result.width != 1:
            raise KeyError(f"Field '{key}' isn't a bit-flag!")
        assert isinstance(result, _BitFlag)
        return result

    def has_field(self, key: _RegistryKey) -> bool:
        """Determine if this manager has a field with this key."""

        name = self.registry.name(key)
        return name is not None and name in self.lookup

    def __getitem__(self, key: _RegistryKey) -> _BitField:
        """Attempt to get a bit-field."""

        result = self.get_field(key)
        if result is None:
            raise KeyError(f"No field '{key}'!")
        return result

    def add_field(self, field: _BitField) -> _Optional[_BitFields]:
        """Add a bit field to the environment."""

        prim = field.raw
        new_primitive = prim not in self.by_primitive
        new_fields = None

        if new_primitive:
            new_fields = _BitFields.new()
            new_fields.raw = prim
            self.by_primitive[prim] = new_fields

        self.by_primitive[prim].claim_field(field)

        # self.add(new_fields, finalize=False)
        return new_fields
