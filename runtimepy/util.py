"""
A module implementing package utilities.
"""


class Identifier:
    """A simple message indentifier interface."""

    def __init__(self) -> None:
        """Initialize this instance."""
        self.curr_id: int = 1
        self.scale = 2

    def __call__(self) -> int:
        """Get the next identifier."""
        curr = self.curr_id
        self.curr_id += self.scale
        return curr
