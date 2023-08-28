"""
A basic type-system implementation.
"""

# built-in
from typing import Dict, Optional

# third-party
from vcorelib.namespace import CPP_DELIM, Namespace

# internal
from runtimepy.codec.protocol import Protocol
from runtimepy.enum import RuntimeEnum
from runtimepy.enum.registry import EnumRegistry
from runtimepy.primitives.byte_order import ByteOrder
from runtimepy.primitives.type import AnyPrimitiveType, PrimitiveTypes


class CustomType:
    """TODO."""

    def __init__(self, protocol: Protocol) -> None:
        """Initialize this instance."""

        self.protocol = protocol


class TypeSystem:
    """A class for managing a custom type system."""

    def __init__(self, *namespace: str) -> None:
        """Initialize this instance."""

        self.primitives: Dict[str, AnyPrimitiveType] = {}
        self.custom: Dict[str, CustomType] = {}

        global_namespace = Namespace(delim=CPP_DELIM)

        # Register global names.
        for name, kind in PrimitiveTypes.items():
            self.primitives[global_namespace.namespace(name)] = kind

        self.root_namespace = global_namespace.child(*namespace)

        # Register enums.
        self._enums = EnumRegistry()
        self.runtime_enum(
            "ByteOrder", ByteOrder.register_enum(self._enums, name="ByteOrder")
        )

    def register(self, name: str) -> CustomType:
        """Register a custom type."""

        new_type = CustomType(Protocol(self._enums))
        self.custom[self._name(name, check_available=True)] = new_type
        return new_type

    def _find_name(self, name: str, strict: bool = False) -> Optional[str]:
        """Attempt to find a registered name."""

        matches = list(self.root_namespace.search(pattern=name))

        assert (
            0 <= len(matches) <= 1
        ), f"Duplicate type names! {name}: {matches}"

        assert not strict or matches, f"Name '{name}' not found."

        return matches[0] if matches else None

    def _name(self, name: str, check_available: bool = False) -> str:
        """Resolve a given name against the current namespace."""

        if check_available:
            resolved = self._find_name(name)
            assert (
                resolved is None
            ), f"Name '{name}' not available! found '{resolved}'"

        return self.root_namespace.namespace(name)

    def _register_primitive(self, name: str, kind: str) -> None:
        """TODO."""

        assert name not in self.primitives, name
        self.primitives[name] = PrimitiveTypes[kind]

    def runtime_enum(self, name: str, enum: RuntimeEnum) -> bool:
        """Register an enumeration."""

        name = self._name(name, check_available=True)

        result = self._enums.register(name, enum)

        if result:
            self._register_primitive(name, enum.primitive)

        return result

    def enum(
        self, name: str, items: Dict[str, int], primitive: str = "uint8"
    ) -> None:
        """Register an enumeration."""

        name = self._name(name, check_available=True)

        enum = self._enums.enum(name, "int", items=items, primitive=primitive)
        assert enum is not None

        # should this call "runtime_enum" ?
        # self.runtime_enum(name, )

        self._register_primitive(name, enum.primitive)

    def size(self, name: str) -> int:
        """Get the size of a named type."""

        found = self._find_name(name, strict=True)
        assert found is not None

        if found in self.primitives:
            return self.primitives[found].size

        return self.custom[found].protocol.array.length()
