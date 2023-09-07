"""
Test the 'tui.cursor' module.
"""

# built-in
from typing import Tuple

# module under test
from runtimepy.tui.cursor import Cursor


class WindowMock:
    """A simple window mock."""

    def __init__(self, width: int = 64, height: int = 64) -> None:
        """Initialize this instance."""

        self.y = 0
        self.x = 0
        self.max_x = width
        self.max_y = height

    def move(self, y: int, x: int) -> None:
        """Move the mocked cursor."""

        assert y < self.max_y, (y, self.max_y)
        assert x < self.max_x, (x, self.max_x)
        self.y = y
        self.x = x

    def getmaxyx(self) -> Tuple[int, int]:
        """Get maximum x and y position."""

        return self.max_y, self.max_x


def test_cursor_basic():
    """Test basic cursor interactions."""

    cursor = Cursor(WindowMock())
    cursor.inc_x()
    cursor.inc_y()
