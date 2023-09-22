"""
A module implementing package utilities.
"""

# built-in
from typing import NamedTuple


class StrToBool(NamedTuple):
    """A container for results when converting strings to boolean."""

    result: bool
    valid: bool

    @staticmethod
    def parse(data: str) -> "StrToBool":
        """Parse a string to boolean."""

        data = data.lower()
        is_true = data == "true"
        resolved = is_true or data == "false"
        return StrToBool(is_true, resolved)
