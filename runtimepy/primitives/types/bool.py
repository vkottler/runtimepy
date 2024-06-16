"""
A module implementing a type interface for booleans.
"""

# internal
from runtimepy.primitives.types.base import BoolCtype as _BoolCtype
from runtimepy.primitives.types.base import PrimitiveType as _PrimitiveType


class BooleanType(_PrimitiveType[_BoolCtype]):
    """A simple type interface for booleans."""

    name = "bool"
    c_type = _BoolCtype
    python_type = bool

    def __init__(self) -> None:
        """Initialize this type."""
        super().__init__("?", signed=False)
        assert self.is_boolean


Bool = BooleanType()
