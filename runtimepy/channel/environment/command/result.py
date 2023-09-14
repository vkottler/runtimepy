"""
A module implementing a command result interface.
"""

# built-in
from typing import NamedTuple, Optional


class CommandResult(NamedTuple):
    """A container for command result data."""

    success: bool
    reason: Optional[str] = None

    def __bool__(self) -> bool:
        """Evaluate this instance as a boolean."""
        return self.success

    def __str__(self) -> str:
        """Get this command result as a string."""

        message = "(success)" if self.success else "(failure)"

        if self.reason:
            message += " " + self.reason

        return message


SUCCESS = CommandResult(True)
