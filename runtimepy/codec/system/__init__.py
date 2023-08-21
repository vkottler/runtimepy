"""
A basic type-system implementation.
"""

# built-in
from typing import Dict

# third-party
from vcorelib.namespace import CPP_DELIM, Namespace

# internal
from runtimepy.codec.protocol import Protocol
from runtimepy.enum import RuntimeEnum
from runtimepy.enum.registry import EnumRegistry
from runtimepy.primitives.byte_order import ByteOrder
from runtimepy.primitives.type import AnyPrimitiveType, PrimitiveTypes


class TypeSystem:
    """A class for managing a custom type system."""

    def __init__(self, *namespace: str) -> None:
        """Initialize this instance."""

        self.primitives: Dict[str, AnyPrimitiveType] = {}
        self.custom: Dict[str, Protocol] = {}

        global_namespace = Namespace(delim=CPP_DELIM)

        # Register global names.
        for name, kind in PrimitiveTypes.items():
            self.primitives[global_namespace.namespace(name)] = kind

        self.root_namespace = global_namespace.child(*namespace)

        # Register enums.
        self._enums = EnumRegistry()
        self.register_enum(
            "ByteOrder", ByteOrder.register_enum(self._enums, name="ByteOrder")
        )

    def register(self, name: str) -> Protocol:
        """Register a custom type."""

        new_type = Protocol(self._enums)
        name = self.root_namespace.namespace(name)
        self.custom[name] = new_type
        return new_type

    def register_enum(self, name: str, enum: RuntimeEnum) -> bool:
        """Register an enumeration."""

        name = self.root_namespace.namespace(name)

        result = self._enums.register(name, enum)

        assert name not in self.primitives, name
        self.primitives[name] = PrimitiveTypes[enum.primitive]

        return result

    def size(self, name: str) -> int:
        """Get the size of a named type."""

        matches = list(self.root_namespace.search(pattern=name))
        assert len(matches) == 1, f"Duplicate type names {name}: {matches}"
        name = matches[0]

        if name in self.primitives:
            return self.primitives[name].size

        return self.custom[name].array.size
