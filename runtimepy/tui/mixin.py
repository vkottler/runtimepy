"""
A module for terminal user-interface application mixins.
"""

# built-in
from contextlib import suppress
from typing import Optional

# internal
from runtimepy.tui.cursor import CursesWindow, Cursor

__all__ = ["CursesWindow", "Cursor", "TuiMixin"]

_curses = {}  # type: ignore
with suppress(ModuleNotFoundError):
    import curses as _curses  # type: ignore


class TuiMixin:
    """A class mixin for building TUI applications."""

    cursor: Cursor

    def __init__(self, window: Optional[CursesWindow] = None) -> None:
        """Initialize this instance."""

        self._window = None
        self.init(window)

    def init(self, window: Optional[CursesWindow]) -> bool:
        """Initialize this interface's window."""

        do_init = window is not None and self._window is None

        if do_init:
            assert window is not None
            self._window = window
            self.cursor = Cursor(self._window)

            # _curses.use_default_colors()
            getattr(_curses, "use_default_colors")()

            # _curses.curs_set(0)
            getattr(_curses, "curs_set")(0)

            # Don't block when getting a character.
            window.nodelay(True)

            # Initialize the window dimensions.
            self.update_dimensions()

        return do_init

    @property
    def window(self) -> CursesWindow:
        """Get the window for this instance."""

        assert self._window is not None
        return self._window

    def update_dimensions(self) -> CursesWindow:
        """Handle an update to the window's dimensions."""

        window = self.window
        self.cursor.poll_max()
        return window

    def tui_update(self) -> None:
        """Re-draw the screen."""

        getattr(_curses, "doupdate")()

    async def handle_char(self, char: int) -> bool:
        """Handle character input."""

        handled = False

        if char != -1:
            if char == getattr(_curses, "KEY_RESIZE"):
                self.update_dimensions()
                handled = True

        return handled
