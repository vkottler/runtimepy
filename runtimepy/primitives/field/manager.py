"""
A management entity for bit-fields.
"""

# built-in
from typing import Dict as _Dict
from typing import Iterable as _Iterable
from typing import List as _List
from typing import Optional as _Optional
from typing import Union as _Union

# internal
from runtimepy.enum import RuntimeEnum as _RuntimeEnum
from runtimepy.enum.registry import EnumRegistry as _EnumRegistry
from runtimepy.primitives.field import BitField as _BitField
from runtimepy.primitives.field import BitFlag as _BitFlag
from runtimepy.primitives.field.fields import BitFields as _BitFields
from runtimepy.registry.name import NameRegistry as _NameRegistry
from runtimepy.registry.name import RegistryKey as _RegistryKey


class BitFieldsManager:
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

        self.fields: _List[_BitFields] = []
        self.lookup: _Dict[str, int] = {}
        self.enum_lookup: _Dict[str, _RuntimeEnum] = {}

        # Add initial fields.
        for field in fields:
            self.add(field)

    def add(self, fields: _BitFields) -> None:
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

    def set(self, key: _RegistryKey, value: _Union[int, bool, str]) -> None:
        """Set a value of a field."""

        field = self[key]

        if isinstance(value, str):
            value = self.enum_lookup[field.name].get_int(value)

        # Update the value.
        field(int(value))

    def get(
        self, key: _RegistryKey, resolve_enum: bool = True
    ) -> _Union[int, str]:
        """Get the value of a field."""

        field = self[key]
        value: _Union[int, str] = field()

        if field.is_enum and resolve_enum:
            value = self.enum_lookup[field.name].get_str(value)

        return value

    def values(
        self, resolve_enum: bool = True
    ) -> _Dict[str, _Union[str, int]]:
        """Get a new dictionary of current field values."""

        return {
            name: self.get(name, resolve_enum=resolve_enum)
            for name in self.lookup
        }

    def has_field(self, key: _RegistryKey) -> bool:
        """Determine if this manager has a field with this key."""

        name = self.registry.name(key)
        return name is not None and name in self.lookup

    def get_field(self, key: _RegistryKey) -> _Optional[_BitField]:
        """Attempt to get a bit-field."""

        result = None
        name = self.registry.name(key)

        if name is not None and name in self.lookup:
            result = self.fields[self.lookup[name]][name]

        return result

    def __getitem__(self, key: _RegistryKey) -> _BitField:
        """Attempt to get a bit-field."""

        result = self.get_field(key)
        if result is None:
            raise KeyError(f"No field '{key}'!")
        return result

    def get_flag(self, key: _RegistryKey) -> _BitFlag:
        """Attempt to lookup a bit-flag."""

        result = self[key]
        if result.width != 1:
            raise KeyError(f"Field '{key}' isn't a bit-flag!")
        assert isinstance(result, _BitFlag)
        return result
