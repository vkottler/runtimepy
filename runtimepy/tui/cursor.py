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

    def move(self, new_y: int = None, new_x: int = None) -> bool:
        """Perform the underlying cursor move."""

        if new_y is None:
            new_y = self.y.value
        if new_x is None:
            new_x = self.x.value

        result = new_y < self.height and new_x < self.width
        if result:
            self.window.move(new_y, new_x)
            self.y.value = new_y
            self.x.value = new_x

        return result

    def poll_max(self) -> bool:
        """Update the min and max cursor positions."""

        curr_width = self.width
        curr_height = self.height

        # Update underlying values.
        self.max_y.value, self.max_x.value = self.window.getmaxyx()

        changed = curr_width != self.width or curr_height != self.height
        if changed:
            self.window.resize(self.height, self.width)

        return changed

    @property
    def width(self) -> int:
        """Get the width of this cursor's window."""
        return self.max_x.value

    @property
    def height(self) -> int:
        """Get the height of this cursor's window."""
        return self.max_y.value

    def reset(self) -> None:
        """Reset this cursor."""

        self.x.value = 0
        self.y.value = 0
        self.poll_max()
        assert self.move()

    def inc_x(self, amount: int = 1) -> bool:
        """Increment the cursor's X coordinate."""

        return self.move(new_x=self.x.value + amount)

    def inc_y(self, amount: int = 1) -> bool:
        """Increment the cursor's Y coordinate."""
        return self.move(new_y=self.y.value + amount)
