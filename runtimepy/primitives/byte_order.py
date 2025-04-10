"""
A module implementing an enumeration for byte ordering options.
"""

# built-in
from typing import Optional

# internal
from runtimepy.enum.registry import EnumRegistry, RuntimeIntEnum


class ByteOrder(RuntimeIntEnum):
    """An enumeration for viable byte orders."""

    NATIVE = 1
    LITTLE_ENDIAN = 2
    BIG_ENDIAN = 3
    NETWORK = 4

    @property
    def fmt(self) -> str:
        """Get the struct formatter for this byte order."""

        if self is ByteOrder.NATIVE:
            return "@"
        if self is ByteOrder.LITTLE_ENDIAN:
            return "<"
        if self is ByteOrder.BIG_ENDIAN:
            return ">"
        return "!"

    def __str__(self) -> str:
        """Get this byte order as a string."""
        return self.fmt

    @classmethod
    def id(cls) -> Optional[int]:
        """Override in sub-class to coerce enum id."""
        return 1


# https://en.cppreference.com/w/cpp/types/endian
STD_ENDIAN = {
    "little": ByteOrder.LITTLE_ENDIAN,
    "big": ByteOrder.BIG_ENDIAN,
    "native": ByteOrder.NATIVE,
}


DEFAULT_BYTE_ORDER = ByteOrder.NETWORK


def enum_registry(
    *kinds: type[RuntimeIntEnum], register_byte_order: bool = True
) -> EnumRegistry:
    """Create an enum registry with the provided custom types registered."""

    result = EnumRegistry()

    if register_byte_order:
        ByteOrder.register_enum(result)

    for kind in kinds:
        kind.register_enum(result)
    return result
