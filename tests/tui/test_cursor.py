"""
Test the 'tui.cursor' module.
"""

# module under test
from runtimepy.tui.cursor import Cursor
from runtimepy.tui.mock import WindowMock


def test_cursor_basic():
    """Test basic cursor interactions."""

    cursor = Cursor(WindowMock())
    cursor.inc_x()
    cursor.inc_y()
