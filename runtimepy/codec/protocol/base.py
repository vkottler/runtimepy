"""
A module implementing an interface to build communication protocols.
"""

# built-in
from contextlib import contextmanager
from copy import copy as _copy
from typing import Dict as _Dict
from typing import Iterator as _Iterator
from typing import List as _List
from typing import NamedTuple
from typing import Optional as _Optional
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# third-party
from vcorelib.io.types import JsonObject as _JsonObject

# internal
from runtimepy.enum import RuntimeEnum as _RuntimeEnum
from runtimepy.enum.registry import EnumRegistry as _EnumRegistry
from runtimepy.primitives import AnyPrimitive as _AnyPrimitive
from runtimepy.primitives import Primitivelike as _Primitivelike
from runtimepy.primitives import create as _create
from runtimepy.primitives.array import PrimitiveArray
from runtimepy.primitives.byte_order import (
    DEFAULT_BYTE_ORDER as _DEFAULT_BYTE_ORDER,
)
from runtimepy.primitives.byte_order import ByteOrder as _ByteOrder
from runtimepy.primitives.field.fields import BitFields as _BitFields
from runtimepy.primitives.field.manager import BitFieldsManager
from runtimepy.registry.name import NameRegistry as _NameRegistry
from runtimepy.registry.name import RegistryKey as _RegistryKey

ProtocolPrimitive = _Union[int, float, bool, str]


class FieldSpec(NamedTuple):
    """Information specifying a protocol field."""

    name: str
    kind: _Primitivelike
    enum: _Optional[_RegistryKey] = None

    def asdict(self) -> _JsonObject:
        """Obtain a dictionary representing this instance."""

        result: _JsonObject = {
            "name": self.name,
            "kind": _create(self.kind).kind.name,
        }
        if self.enum is not None:
            result["enum"] = self.enum
        return result


T = _TypeVar("T", bound="ProtocolBase")


class ProtocolBase:
    """A class for defining runtime communication protocols."""

    def __init__(
        self,
        enum_registry: _EnumRegistry,
        names: _NameRegistry = None,
        fields: BitFieldsManager = None,
        build: _List[_Union[int, FieldSpec]] = None,
        identifier: int = 1,
        byte_order: _Union[_ByteOrder, _RegistryKey] = _DEFAULT_BYTE_ORDER,
    ) -> None:
        """Initialize this protocol."""

        self.id = identifier

        # Register the byte-order enumeration if it's not present.
        self._enum_registry = enum_registry
        if not self._enum_registry.get("ByteOrder"):
            _ByteOrder.register_enum(self._enum_registry)

        # Each instance gets its own array.
        if not isinstance(byte_order, _ByteOrder):
            byte_order = _ByteOrder(
                self._enum_registry["ByteOrder"].get_int(byte_order)
            )
        self.array = PrimitiveArray(byte_order=byte_order)

        if names is None:
            names = _NameRegistry()
        self._names = names

        if fields is None:
            fields = BitFieldsManager(self._names, self._enum_registry)
        self._fields = fields

        self._regular_fields: _Dict[str, _AnyPrimitive] = {}
        self._enum_fields: _Dict[str, _RuntimeEnum] = {}

        # Keep track of the order that the protocol was created.
        if build is None:
            build = []
        self._build: _List[_Union[int, FieldSpec]] = build

        # Add fields if necessary.
        for item in self._build:
            if isinstance(item, int):
                self._add_bit_fields(self._fields.fields[item], track=False)
            else:
                self.add_field(
                    item.name, item.kind, enum=item.enum, track=False
                )

    def __copy__(self: T) -> T:
        """Create another protocol instance from this one."""

        return self.__class__(
            self._enum_registry,
            names=self._names,
            fields=_copy(self._fields),
            build=self._build,
            byte_order=self.array.byte_order,
        )

    def add_field(
        self,
        name: str,
        kind: _Primitivelike,
        enum: _RegistryKey = None,
        track: bool = True,
    ) -> None:
        """Add a new field to the protocol."""

        # Register the field name.
        ident = self._names.register_name(name)
        assert ident is not None, f"Couldn't register field '{name}'!"

        new = _create(kind)
        self.array.add(new)
        self._regular_fields[name] = new
        if enum is not None:
            self._enum_fields[name] = self._enum_registry[enum]

        if track:
            self._build.append(FieldSpec(name, kind, enum))

    def _add_bit_fields(self, fields: _BitFields, track: bool = True) -> None:
        """Add a bit-fields instance."""

        idx = self._fields.add(fields)
        self.array.add(fields.raw)
        if track:
            self._build.append(idx)

    @contextmanager
    def add_bit_fields(
        self, kind: _Primitivelike = "uint8"
    ) -> _Iterator[_BitFields]:
        """Add a bit-fields primitive to the protocol."""

        new = _BitFields.new(value=kind)
        yield new
        self._add_bit_fields(new)

    def value(self, name: str, resolve_enum: bool = True) -> ProtocolPrimitive:
        """Get the value of a field belonging to the protocol."""

        val: ProtocolPrimitive = 0

        if name in self._regular_fields:
            val = self._regular_fields[name].value

            # Resolve the enum value.
            if resolve_enum and name in self._enum_fields:
                val = self._enum_fields[name].get_str(val)  # type: ignore

            return val

        return self._fields.get(name, resolve_enum=resolve_enum)

    def __getitem__(self, name: str) -> ProtocolPrimitive:
        """Get the value of a protocol field."""
        return self.value(name)

    def __setitem__(self, name: str, val: ProtocolPrimitive) -> None:
        """Set a value of a field belonging to the protocol."""

        if name in self._regular_fields:
            # Resolve an enum value.
            if isinstance(val, str):
                val = self._enum_fields[name].get_int(val)
            self._regular_fields[name].value = val
        else:
            self._fields.set(name, val)  # type: ignore
