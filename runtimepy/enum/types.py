"""
A module implementing a type system for runtime enumerations.
"""

# built-in
from enum import Enum as _Enum
from typing import Union as _Union

EnumTypelike = _Union[str, "EnumType"]


class EnumType(_Enum):
    """An enumeration containing the types of runtime enumerations."""

    BOOL = "bool"
    INT = "int"

    def __str__(self) -> str:
        """Get this enum type as a string."""
        return self.value

    def valid(self, val: _Union[int, bool]) -> bool:
        """Determine if a value is valid based on this enumeration."""
        return isinstance(val, bool if self is EnumType.BOOL else int)

    def validate(self, val: _Union[int, bool]) -> None:
        """Validate a primitive value."""

        if not self.valid(val):
            raise ValueError(f"Value '{val}' is not {self.value}!")

    @staticmethod
    def normalize(val: EnumTypelike) -> "EnumType":
        """Normalize an enumeration type."""

        if isinstance(val, str):
            val = EnumType(val.lower())
        return val
