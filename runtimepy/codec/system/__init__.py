"""
A basic type-system implementation.
"""

# built-in
from contextlib import suppress
from typing import Iterable, Optional, Union

# third-party
from vcorelib.logging import LoggerMixin
from vcorelib.namespace import CPP_DELIM, Namespace

# internal
from runtimepy.codec.protocol import Protocol
from runtimepy.enum import RuntimeEnum
from runtimepy.enum.registry import DEFAULT_ENUM_PRIMITIVE, RuntimeIntEnum
from runtimepy.primitives.byte_order import (
    DEFAULT_BYTE_ORDER,
    ByteOrder,
    enum_registry,
)
from runtimepy.primitives.types import AnyPrimitiveType, PrimitiveTypes
from runtimepy.registry.name import RegistryKey
from runtimepy.util import Identifier


def resolve_name(matches: Iterable[str]) -> str:
    """Resolve a possible name conflict."""

    by_len: dict[int, list[str]] = {}
    shortest = -1
    for match in matches:
        length = len(match)
        if shortest == -1 or length < shortest:
            shortest = length

        by_len.setdefault(length, [])
        by_len[length].append(match)

    result = by_len[shortest]
    assert len(result) == 1, result
    return result[0]


class TypeSystem(LoggerMixin):
    """A class for managing a custom type system."""

    def __init__(self, *namespace: str) -> None:
        """Initialize this instance."""

        super().__init__()

        self.primitives: dict[str, AnyPrimitiveType] = {}
        self.custom: dict[str, Protocol] = {}
        self.custom_ids = Identifier(scale=1)

        self._enums = enum_registry(register_byte_order=False)

        global_namespace = Namespace(delim=CPP_DELIM)

        # Register global names.
        for name, kind in PrimitiveTypes.items():
            self.primitives[global_namespace.namespace(name)] = kind

        self.root_namespace = global_namespace

        # Register enums.
        for enum in [ByteOrder]:
            self.runtime_int_enum(enum)

        self.root_namespace = global_namespace.child(*namespace)

    def is_enum(self, name: str, *namespace: str, exact: bool = True) -> bool:
        """Determine if the arguments identify a registered enumeration."""

        result = False

        with suppress(KeyError, AssertionError):
            self.get_enum(name, *namespace, exact=exact)
            result = True

        return result

    def get_enum(
        self, name: str, *namespace: str, exact: bool = True
    ) -> RuntimeEnum:
        """Lookup an enum type at runtime."""

        found = self._find_name(name, *namespace, strict=True, exact=exact)
        assert found is not None
        return self._enums[found]

    def runtime_int_enum(self, enum: type[RuntimeIntEnum]) -> None:
        """Register an enumeration class."""

        name = self._name(enum.enum_name(), check_available=True)
        runtime = enum.register_enum(self._enums, name=name)
        self._register_primitive(name, runtime.primitive)

    def enum(
        self,
        name: str,
        items: dict[str, int],
        *namespace: str,
        primitive: str = DEFAULT_ENUM_PRIMITIVE,
    ) -> None:
        """Register an enumeration."""

        name = self._name(name, *namespace, check_available=True)

        enum = self._enums.enum(name, "int", items=items, primitive=primitive)
        assert enum is not None
        self._register_primitive(name, enum.primitive)

    def register(
        self,
        name: str,
        *namespace: str,
        byte_order: Union[ByteOrder, RegistryKey] = DEFAULT_BYTE_ORDER,
    ) -> Protocol:
        """Register a custom type."""

        resolved = self._name(name, *namespace, check_available=True)
        new_type = Protocol(
            self._enums,
            alias=resolved,
            identifier=self.custom_ids(),
            byte_order=byte_order,
        )
        self.custom[resolved] = new_type
        return new_type

    def is_custom(
        self, name: str, *namespace: str, exact: bool = True
    ) -> bool:
        """Determine if the parameters identify a custom type."""

        result = False

        with suppress(KeyError, AssertionError):
            self.get_protocol(name, *namespace, exact=exact)
            result = True

        return result

    def get_protocol(
        self, name: str, *namespace: str, exact: bool = True
    ) -> Protocol:
        """Get a custom protocol by name."""

        found = self._find_name(name, *namespace, strict=True, exact=exact)
        assert found is not None
        return self.custom[found]

    def add(
        self,
        custom_type: str,
        field_name: str,
        field_type: str,
        array_length: int = None,
        exact: bool = True,
    ) -> None:
        """Add a field to a custom type."""

        type_name = self._find_name(custom_type, strict=True, exact=exact)
        assert type_name is not None
        field_type_name = self._find_name(field_type, strict=True, exact=exact)
        assert field_type_name is not None

        assert type_name in self.custom, type_name
        custom = self.custom[type_name]

        # Handle enumerations.
        enum = self._enums.get(field_type_name)
        if enum is not None:
            custom.add_field(
                field_name, enum=field_type_name, array_length=array_length
            )
            return

        # Lookup field type.
        if field_type_name in self.custom:
            custom.add_serializable(
                field_name,
                self.custom[field_type_name].copy(),
                array_length=array_length,
            )
        else:
            custom.add_field(
                field_name,
                kind=self.primitives[field_type_name].name,
                array_length=array_length,
            )

    def _find_name(
        self,
        name: str,
        *namespace: str,
        strict: bool = False,
        exact: bool = True,
    ) -> Optional[str]:
        """Attempt to find a registered name."""

        if name in self.primitives:
            return name

        with self.root_namespace.pushed(*namespace):
            candidate = self.root_namespace.namespace(name, track=False)
            if candidate in self.custom:
                return candidate

            matches = list(
                x
                for x in self.root_namespace.search(pattern=name)
                if not exact or x == candidate
            )

        match = (
            resolve_name(matches)
            if not 0 <= len(matches) <= 1
            else (matches[0] if matches else None)
        )

        assert not strict or match, f"Name '{name}' not found."
        return match

    def _name(
        self, name: str, *namespace: str, check_available: bool = False
    ) -> str:
        """Resolve a given name against the current namespace."""

        with self.root_namespace.pushed(*namespace):
            if check_available:
                resolved = self._find_name(name)
                assert (
                    resolved is None
                    or self.root_namespace.namespace(name, track=False)
                    != resolved
                ), f"Name '{name}' not available! found '{resolved}'"

            result = self.root_namespace.namespace(name)

        return result

    def _register_primitive(self, name: str, kind: str) -> None:
        """Register a type alias for a primitive value."""

        assert name not in self.primitives, name
        self.primitives[name] = PrimitiveTypes[kind]

    def size(
        self,
        name: str,
        *namespace: str,
        trace: bool = False,
        exact: bool = True,
    ) -> int:
        """Get the size of a named type."""

        found = self._find_name(name, *namespace, strict=True, exact=exact)
        assert found is not None

        if found in self.primitives:
            return self.primitives[found].size

        if trace:
            self.custom[found].trace_size(self.logger)

        return self.custom[found].length()
