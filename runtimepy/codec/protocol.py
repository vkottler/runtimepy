"""
A module implementing an interface to build communication protocols.
"""

# built-in
from typing import Dict as _Dict
from typing import Set as _Set

# internal
from runtimepy.enum import RuntimeEnum as _RuntimeEnum
from runtimepy.enum.registry import EnumRegistry as _EnumRegistry
from runtimepy.primitives import Primitivelike as _Primitivelike
from runtimepy.primitives import create as _create
from runtimepy.primitives.array import PrimitiveArray
from runtimepy.primitives.field.fields import BitFields as _BitFields
from runtimepy.primitives.field.manager import BitFieldsManager
from runtimepy.registry.name import NameRegistry as _NameRegistry
from runtimepy.registry.name import RegistryKey as _RegistryKey


class Protocol:
    """A class for defining runtime communication protocols."""

    def __init__(self, enum_registry: _EnumRegistry) -> None:
        """Initialize this protocol."""

        self.array = PrimitiveArray()
        self.enum_registry = enum_registry
        self.names = _NameRegistry()
        self.fields = BitFieldsManager(self.names, self.enum_registry)
        self.regular_fields: _Set[str] = set()
        self.enum_fields: _Dict[str, _RuntimeEnum] = {}

    def add_field(
        self, name: str, kind: _Primitivelike, enum: _RegistryKey = None
    ) -> None:
        """Add a new field to the protocol."""

        new = _create(kind)
        self.array.add(new)
        self.regular_fields.add(name)
        if enum is not None:
            self.enum_fields[name] = self.enum_registry[enum]

    def add_bit_fields(self, kind: _Primitivelike = "uint8") -> _BitFields:
        """Add a bit-fields primitive to the protocol."""

        new = _BitFields.new(value=kind)
        self.fields.add(new)
        self.array.add(new.raw)
        return new
