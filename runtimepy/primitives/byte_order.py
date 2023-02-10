"""
A module implementing an enumeration for byte ordering options.
"""

# internal
from runtimepy.enum.registry import RuntimeIntEnum as _RuntimeIntEnum


class ByteOrder(_RuntimeIntEnum):
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


DEFAULT_BYTE_ORDER = ByteOrder.NETWORK
