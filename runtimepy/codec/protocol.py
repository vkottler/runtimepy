"""
A module implementing an interface to build communication protocols.
"""

# built-in
from contextlib import contextmanager
from typing import Dict as _Dict
from typing import Iterator as _Iterator
from typing import Union as _Union

# internal
from runtimepy.enum import RuntimeEnum as _RuntimeEnum
from runtimepy.enum.registry import EnumRegistry as _EnumRegistry
from runtimepy.primitives import AnyPrimitive as _AnyPrimitive
from runtimepy.primitives import Primitivelike as _Primitivelike
from runtimepy.primitives import create as _create
from runtimepy.primitives.array import PrimitiveArray
from runtimepy.primitives.field.fields import BitFields as _BitFields
from runtimepy.primitives.field.manager import BitFieldsManager
from runtimepy.registry.name import NameRegistry as _NameRegistry
from runtimepy.registry.name import RegistryKey as _RegistryKey

ProtocolPrimitive = _Union[int, float, bool, str]


class Protocol:
    """A class for defining runtime communication protocols."""

    def __init__(self, enum_registry: _EnumRegistry) -> None:
        """Initialize this protocol."""

        self.array = PrimitiveArray()
        self.enum_registry = enum_registry
        self.names = _NameRegistry()
        self.fields = BitFieldsManager(self.names, self.enum_registry)
        self.regular_fields: _Dict[str, _AnyPrimitive] = {}
        self.enum_fields: _Dict[str, _RuntimeEnum] = {}

    def add_field(
        self, name: str, kind: _Primitivelike, enum: _RegistryKey = None
    ) -> None:
        """Add a new field to the protocol."""

        new = _create(kind)
        self.array.add(new)
        self.regular_fields[name] = new
        if enum is not None:
            self.enum_fields[name] = self.enum_registry[enum]

    @contextmanager
    def add_bit_fields(
        self, kind: _Primitivelike = "uint8"
    ) -> _Iterator[_BitFields]:
        """Add a bit-fields primitive to the protocol."""

        new = _BitFields.new(value=kind)
        yield new
        self.fields.add(new)
        self.array.add(new.raw)

    def value(self, name: str, resolve_enum: bool = True) -> ProtocolPrimitive:
        """Get the value of a field belonging to the protocol."""

        val: ProtocolPrimitive = 0

        if name in self.regular_fields:
            val = self.regular_fields[name].value

            # Resolve the enum value.
            if resolve_enum and name in self.enum_fields:
                val = self.enum_fields[name].get_str(val)  # type: ignore

            return val

        field = self.fields[name]
        val = field()

        # Resolve the enum value.
        if resolve_enum and field.is_enum:
            val = self.enum_registry[field.enum].get_str(val)
        elif field.width == 1:
            val = bool(val)

        return val

    def __getitem__(self, name: str) -> ProtocolPrimitive:
        """Get the value of a protocol field."""
        return self.value(name)

    def __setitem__(self, name: str, val: ProtocolPrimitive) -> None:
        """Set a value of a field belonging to the protocol."""

        if name in self.regular_fields:
            # Resolve an enum value.
            if isinstance(val, str):
                val = self.enum_fields[name].get_int(val)
            self.regular_fields[name].value = val
        else:
            field = self.fields[name]

            # Resolve an enum value.
            if isinstance(val, str):
                val = self.enum_registry[field.enum].get_int(val)

            field(val=int(val))
