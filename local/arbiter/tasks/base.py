"""
A module implementing a base application.
"""

# built-in
import curses

# internal
from runtimepy.net.arbiter import AppInfo
from runtimepy.net.arbiter.task import ArbiterTask
from runtimepy.tui.mixin import CursesWindow


class AppBase(ArbiterTask):
    """A base TUI application."""

    app: AppInfo

    async def init(self, app: AppInfo) -> None:
        """Initialize this task with application information."""

        self.app = app
        self._handle_resize()

    def _handle_resize(self) -> None:
        """Handle the application getting re-sized."""

        self.app.tui.update_dimensions()

    def handle_char(self, char: int) -> None:
        """Handle user input."""

        if char == curses.KEY_RESIZE:
            self._handle_resize()

        elif char == curses.KEY_MOUSE:
            pass

        else:
            # trigger this with 'q'
            self.app.stop.set()

    def draw(self, window: CursesWindow) -> None:
        """Draw the application."""

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

        window = self.window

        # Handle input.
        data = window.getch()
        if data != -1:
            self.handle_char(data)

        # Update state.
        self.draw(window)
        window.noutrefresh()
        curses.doupdate()

        return True

    @property
    def window(self) -> CursesWindow:
        """Get this instance's window."""
        return self.app.tui.window
