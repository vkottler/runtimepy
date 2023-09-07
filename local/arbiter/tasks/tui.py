"""
A module implementing a basic TUI application.
"""

# internal
from runtimepy.net.arbiter import AppInfo
from runtimepy.tui.mixin import CursesWindow

# local
from .base import AppBase


class App(AppBase):
    """A simple TUI application."""

    async def init(self, app: AppInfo) -> None:
        """Initialize this task with application information."""

        await super().init(app)

        for name, conn in self.app.connections.items():
            print(name)
            print(conn)

    def _handle_resize(self) -> None:
        """Handle the application getting re-sized."""

        super()._handle_resize()

        self.window.clear()

    def draw_metrics(
        self, start_y: int, start_x: int, window: CursesWindow
    ) -> None:
        """Draw metrics."""

        window.addstr(
            start_y,
            start_x,
            f"dispatches {self.metrics.dispatches.value:10.5f}",
        )
        window.addstr(
            start_y + 1,
            start_x,
            f"rate_hz    {self.metrics.rate_hz.value:10.5f}",
        )
        window.addstr(
            start_y + 2,
            start_x,
            f"average_s  {self.metrics.average_s.value:10.5f}",
        )
        window.addstr(
            start_y + 3,
            start_x,
            f"max_s      {self.metrics.max_s.value:10.5f}",
        )
        window.addstr(
            start_y + 4,
            start_x,
            f"min_s      {self.metrics.min_s.value:10.5f}",
        )

    def draw(self, window: CursesWindow) -> None:
        """Draw the application."""

        self.draw_metrics(0, 0, window)
