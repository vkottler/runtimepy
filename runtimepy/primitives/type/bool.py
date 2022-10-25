"""
A module implementing a type interface for booleans.
"""

# internal
from runtimepy.primitives.type.base import BoolCtype as _BoolCtype
from runtimepy.primitives.type.base import PrimitiveType as _PrimitiveType


class BooleanType(_PrimitiveType[_BoolCtype]):
    """A simple type interface for booleans."""

    name = "bool"
    c_type = _BoolCtype

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__("?")
        assert self.is_boolean


Bool = BooleanType()
