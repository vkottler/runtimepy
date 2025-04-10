"""
A module implementing an interface to build communication protocols.
"""

# built-in
from contextlib import contextmanager, suppress
from copy import copy as _copy
from io import StringIO
from typing import Iterator as _Iterator
from typing import NamedTuple
from typing import Optional as _Optional
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# third-party
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.logging import LoggerType

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
from runtimepy.primitives.serializable import Serializable, SerializableMap
from runtimepy.registry.name import NameRegistry as _NameRegistry
from runtimepy.registry.name import RegistryKey as _RegistryKey

ProtocolPrimitive = _Union[int, float, bool, str]


class FieldSpec(NamedTuple):
    """Information specifying a protocol field."""

    name: str
    kind: _Primitivelike
    enum: _Optional[_RegistryKey] = None
    array_length: _Optional[int] = None

    def asdict(self) -> _JsonObject:
        """Obtain a dictionary representing this instance."""

        result: _JsonObject = {
            "name": self.name,
            "kind": _create(self.kind).kind.name,
            "array_length": self.array_length,
        }
        if self.enum is not None:
            result["enum"] = self.enum
        return result


T = _TypeVar("T", bound="ProtocolBase")
ProtocolBuild = list[_Union[int, FieldSpec, tuple[str, int]]]


class ProtocolBase(PrimitiveArray):
    """A class for defining runtime communication protocols."""

    def __init__(
        self,
        enum_registry: _EnumRegistry,
        names: _NameRegistry = None,
        fields: BitFieldsManager = None,
        build: ProtocolBuild = None,
        identifier: int = 1,
        byte_order: _Union[_ByteOrder, _RegistryKey] = _DEFAULT_BYTE_ORDER,
        serializables: SerializableMap = None,
        alias: str = None,
    ) -> None:
        """Initialize this protocol."""

        self.id = identifier
        self.alias = alias

        # Register the byte-order enumeration if it's not present.
        self._enum_registry = enum_registry
        if not self._enum_registry.get("ByteOrder"):
            _ByteOrder.register_enum(self._enum_registry)

        # Each instance gets its own array.
        if not isinstance(byte_order, _ByteOrder):
            byte_order = _ByteOrder(
                self._enum_registry["ByteOrder"].get_int(byte_order)
            )

        super().__init__(byte_order=byte_order)

        if names is None:
            names = _NameRegistry()
        self.names = names

        if fields is None:
            fields = BitFieldsManager(self.names, self._enum_registry)
        self._fields = fields

        self._regular_fields: dict[str, list[_AnyPrimitive]] = {}
        self._enum_fields: dict[str, _RuntimeEnum] = {}

        # Keep track of the order that the protocol was created.
        self._build: ProtocolBuild = []

        # Keep track of named serializables.
        self.serializables: SerializableMap = {}

        # Add fields if necessary.
        if build is None:
            build = []
        for item in build:
            if isinstance(item, int):
                self._add_bit_fields(self._fields.fields[item])
            elif isinstance(item, FieldSpec):
                self.add_field(
                    item.name,
                    item.kind,
                    enum=item.enum,
                    array_length=item.array_length,
                )
            else:
                assert serializables, (item, serializables)
                name = item[0]
                self.add_serializable(
                    name,
                    serializables[name][0],
                    array_length=None if item[1] == 1 else item[1],
                )
                del serializables[name]

        # Ensure all serializables were handled via build.
        assert not serializables, serializables

    def _copy_impl(self: T) -> T:
        """Create another protocol instance from this one."""

        return self.__class__(
            self._enum_registry,
            names=self.names,
            fields=_copy(self._fields),
            build=self._build,
            byte_order=self.byte_order,
            identifier=self.id,
            serializables={
                key: [val[0].copy_without_chain()]
                for key, val in self.serializables.items()
            },
            alias=self.alias,
        )

    def register_name(self, name: str) -> int:
        """Register the field name."""

        ident = self.names.register_name(name)
        assert ident is not None, f"Couldn't register field '{name}'!"
        return ident

    def add_serializable(
        self, name: str, serializable: Serializable, array_length: int = None
    ) -> None:
        """Add a serializable instance."""

        self.register_name(name)

        instances = self.add_to_end(serializable, array_length=array_length)
        self._build.append((name, len(instances)))
        self.serializables[name] = instances

    def add_field(
        self,
        name: str,
        kind: _Primitivelike = None,
        enum: _RegistryKey = None,
        serializable: Serializable = None,
        array_length: int = None,
    ) -> None:
        """Add a new field to the protocol."""

        # Add the serializable to the end of this protocol.
        if serializable is not None:
            assert kind is None and enum is None
            self.add_serializable(
                name, serializable, array_length=array_length
            )
            return

        self.register_name(name)

        if enum is not None:
            runtime_enum = self._enum_registry[enum]
            self._enum_fields[name] = runtime_enum

            # Allow the primitive type to be overridden when passed as a
            # method argument.
            if kind is None:
                kind = runtime_enum.primitive

        assert kind is not None

        self._regular_fields[name] = self.add(
            _create(kind), array_length=array_length
        )

        self._build.append(
            FieldSpec(name, kind, enum, array_length=array_length)
        )

    def _add_bit_fields(self, fields: _BitFields) -> None:
        """Add a bit-fields instance."""

        self._build.append(self._fields.add(fields))
        self.add(fields.raw)

    @contextmanager
    def add_bit_fields(
        self, kind: _Primitivelike = "uint8"
    ) -> _Iterator[_BitFields]:
        """Add a bit-fields primitive to the protocol."""

        new = _BitFields.new(value=kind)
        yield new
        self._add_bit_fields(new)

    def value(
        self, name: str, resolve_enum: bool = True, index: int = 0
    ) -> ProtocolPrimitive:
        """Get the value of a field belonging to the protocol."""

        val: ProtocolPrimitive = 0

        if name in self._regular_fields:
            val = self._regular_fields[name][index].value

            # Resolve the enum value.
            if resolve_enum and name in self._enum_fields:
                with suppress(KeyError):
                    val = self._enum_fields[name].get_str(val)  # type: ignore

            return val

        return self._fields.get(name, resolve_enum=resolve_enum)

    def trace_size(self, logger: LoggerType) -> None:
        """Log a size trace."""
        logger.info("%s: %s", self, self.length_trace(alias=self.alias))

    def __str__(self) -> str:
        """Get this instance as a string."""

        with StringIO() as stream:
            stream.write(
                "{"
                + f"{self.resolve_alias(alias=self.alias)}({self.length()}): "
            )

            parts = []
            for name in self.names.registered_order:
                part = name
                count = 1

                if name in self.serializables:
                    count = len(self.serializables[name])
                    part += f"<{self.serializables[name][0].resolve_alias()}>"
                elif name in self._regular_fields:
                    count = len(self._regular_fields[name])

                    part += f"<{self._regular_fields[name][0].kind}>"

                if count > 1:
                    part += f"[{count}] = ["
                    if name in self._regular_fields:
                        part += ", ".join(
                            str(x.value) for x in self._regular_fields[name]
                        )
                    else:
                        part += ", ".join("..." for _ in range(count))
                    part += "]"
                else:
                    part += f" = {self[name]}"

                parts.append(part)

            stream.write(", ".join(parts))

            stream.write("}")

            return stream.getvalue()

    def __getitem__(self, name: str) -> ProtocolPrimitive:  # type: ignore
        """Get the value of a protocol field."""

        if name in self.serializables:
            return str(self.serializables[name][0])

        return self.value(name)

    def set(self, name: str, val: ProtocolPrimitive, index: int = 0) -> None:
        """Set a value of a field belonging to the protocol."""

        if name in self._regular_fields:
            # Resolve an enum value.
            if isinstance(val, str):
                val = self._enum_fields[name].get_int(val)
            self._regular_fields[name][index].value = val
        elif name in self.serializables and isinstance(val, str):
            self.serializables[name][index].update_str(val)
        else:
            self._fields.set(name, val)  # type: ignore

    def __setitem__(self, name: str, val: ProtocolPrimitive) -> None:
        """Set a value of a field belonging to the protocol."""
        self.set(name, val)
