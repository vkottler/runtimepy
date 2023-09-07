"""
A basic cursor implementation for TUIs.
"""

# built-in
from typing import Any

# internal
from runtimepy.primitives import Uint32

# Typing for something like '_curses.window' isn't supported yet.
CursesWindow = Any


class Cursor:
    """A simple cursor implementation."""

    def __init__(self, window: CursesWindow) -> None:
        """Initialize this cursor."""

        self.window = window
        self.x = Uint32()
        self.y = Uint32()
        self.max_x = Uint32()
        self.max_y = Uint32()

        self.reset()

    def _move(self) -> None:
        """Perform the underlying cursor move."""

        assert self.y.value < self.max_y.value
        assert self.x.value < self.max_x.value

        self.window.move(self.y.value, self.x.value)

    def poll_max(self) -> None:
        """Update the min and max cursor positions."""
        self.max_y.value, self.max_x.value = self.window.getmaxyx()

    def reset(self) -> None:
        """Reset this cursor."""

        self.x.value = 0
        self.y.value = 0
        self.poll_max()
        self._move()

    def inc_x(self, amount: int = 1) -> None:
        """Increment the cursor's X coordinate."""
        self.x.value += amount
        self._move()

    def inc_y(self, amount: int = 1) -> None:
        """Increment the cursor's Y coordinate."""
        self.y.value += amount
        self._move()
