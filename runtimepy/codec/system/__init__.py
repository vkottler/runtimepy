"""
A basic type-system implementation.
"""

# built-in
from typing import Dict, Optional, Type

# third-party
from vcorelib.namespace import CPP_DELIM, Namespace

# internal
from runtimepy import PKG_NAME
from runtimepy.codec.protocol import Protocol
from runtimepy.enum import RuntimeEnum
from runtimepy.enum.registry import (
    DEFAULT_ENUM_PRIMITIVE,
    EnumRegistry,
    RuntimeIntEnum,
)
from runtimepy.primitives.byte_order import ByteOrder
from runtimepy.primitives.type import AnyPrimitiveType, PrimitiveTypes


class TypeSystem:
    """A class for managing a custom type system."""

    def __init__(self, *namespace: str) -> None:
        """Initialize this instance."""

        self.primitives: Dict[str, AnyPrimitiveType] = {}
        self.custom: Dict[str, Protocol] = {}
        self._enums = EnumRegistry()

        global_namespace = Namespace(delim=CPP_DELIM)

        # Register global names.
        for name, kind in PrimitiveTypes.items():
            self.primitives[global_namespace.namespace(name)] = kind

        self.root_namespace = global_namespace

        # Register enums.
        with self.root_namespace.pushed(PKG_NAME):
            for enum in [ByteOrder]:
                self.runtime_int_enum(enum)

        self.root_namespace = global_namespace.child(*namespace)

    def get_enum(self, name: str, *namespace: str) -> RuntimeEnum:
        """Lookup an enum type at runtime."""

        found = self._find_name(name, *namespace, strict=True)
        assert found is not None
        return self._enums[found]

    def runtime_int_enum(self, enum: Type[RuntimeIntEnum]) -> None:
        """Register an enumeration class."""

        name = self._name(enum.enum_name(), check_available=True)
        runtime = enum.register_enum(self._enums, name=name)
        self._register_primitive(name, runtime.primitive)

    def enum(
        self,
        name: str,
        items: Dict[str, int],
        *namespace: str,
        primitive: str = DEFAULT_ENUM_PRIMITIVE,
    ) -> None:
        """Register an enumeration."""

        name = self._name(name, *namespace, check_available=True)

        enum = self._enums.enum(name, "int", items=items, primitive=primitive)
        assert enum is not None
        self._register_primitive(name, enum.primitive)

    def register(self, name: str, *namespace: str) -> Protocol:
        """Register a custom type."""

        new_type = Protocol(self._enums)
        self.custom[
            self._name(name, *namespace, check_available=True)
        ] = new_type
        return new_type

    def get_protocol(self, name: str, *namespace: str) -> Protocol:
        """Get a custom protocol by name."""

        found = self._find_name(name, *namespace, strict=True)
        assert found is not None
        return self.custom[found]

    def add(self, custom_type: str, field_name: str, field_type: str) -> None:
        """Add a field to a custom type."""

        type_name = self._find_name(custom_type, strict=True)
        assert type_name is not None
        field_type_name = self._find_name(field_type, strict=True)
        assert field_type_name is not None

        assert type_name in self.custom, type_name
        custom = self.custom[type_name]

        # Handle enumerations.
        enum = self._enums.get(field_type_name)
        if enum is not None:
            custom.add_field(field_name, enum=field_type_name)
            return

        # Lookup field type.
        if field_type_name in self.custom:
            custom.array.add_to_end(self.custom[field_type_name].array.copy())
            return

        custom.add_field(
            field_name, kind=self.primitives[field_type_name].name
        )

    def _find_name(
        self, name: str, *namespace: str, strict: bool = False
    ) -> Optional[str]:
        """Attempt to find a registered name."""

        if name in self.primitives:
            return name

        with self.root_namespace.pushed(*namespace):
            matches = list(self.root_namespace.search(pattern=name))

        assert (
            0 <= len(matches) <= 1
        ), f"Duplicate type names! {name}: {matches}"

        assert not strict or matches, f"Name '{name}' not found."

        return matches[0] if matches else None

    def _name(
        self, name: str, *namespace: str, check_available: bool = False
    ) -> str:
        """Resolve a given name against the current namespace."""

        with self.root_namespace.pushed(*namespace):
            if check_available:
                resolved = self._find_name(name)
                assert (
                    resolved is None
                ), f"Name '{name}' not available! found '{resolved}'"

            result = self.root_namespace.namespace(name)

        return result

    def _register_primitive(self, name: str, kind: str) -> None:
        """Register a type alias for a primitive value."""

        assert name not in self.primitives, name
        self.primitives[name] = PrimitiveTypes[kind]

    def size(self, name: str, *namespace: str) -> int:
        """Get the size of a named type."""

        found = self._find_name(name, *namespace, strict=True)
        assert found is not None

        if found in self.primitives:
            return self.primitives[found].size

        return self.custom[found].size
