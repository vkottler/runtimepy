"""
A module implementing a simple window mock.
"""

# built-in
from contextlib import suppress
from os import environ
from sys import platform
from typing import Tuple

_curses = {}  # type: ignore
with suppress(ModuleNotFoundError):
    import curses as _curses  # type: ignore


class WindowMock:
    """A simple window mock."""

    def __init__(self, width: int = 64, height: int = 64) -> None:
        """Initialize this instance."""

        self.y = 0
        self.x = 0
        self.max_x = width
        self.max_y = height

    def resize(self, nlines: int, ncols: int) -> None:
        """A simple re-size method."""

        self.max_x = ncols
        self.max_y = nlines

    def move(self, y: int, x: int) -> None:
        """Move the mocked cursor."""

        assert y < self.max_y, (y, self.max_y)
        assert x < self.max_x, (x, self.max_x)
        self.y = y
        self.x = x

    def getmaxyx(self) -> Tuple[int, int]:
        """Get maximum x and y position."""

        return self.max_y, self.max_x


def stage_char(data: int) -> None:
    """Stage an input character."""

    # curses.ungetch(data)
    getattr(_curses, "ungetch")(data)


def wrapper_mock(*args, **kwargs) -> None:
    """Create a virtual window."""

    # Set some environment variables if they're not set.
    if platform in ["linux", "darwin"]:
        environ.setdefault("TERMINFO", "/etc/terminfo")
        environ.setdefault("TERM", "linux")

    # Initialize the library (else curses won't work at all).
    getattr(_curses, "initscr")()  # curses.initscr()
    getattr(_curses, "start_color")()  # curses.start_color()

    # Send a re-size event.
    stage_char(getattr(_curses, "KEY_RESIZE"))

    # Create a virtual window for the application to use.
    window = getattr(_curses, "newwin")(24, 80)  # curses.newwin(24, 80)

    args[0](window, *args[1:], **kwargs)
