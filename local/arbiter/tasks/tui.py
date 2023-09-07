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

    def draw(self, window: CursesWindow) -> None:
        """Draw the application."""

        self.cursor.reset()

        for env in [self.env]:
            for name in env.names:
                line = name

                chan, enum = self.env[name]

                # do floats better
                line += " " + str(chan)

                if enum is not None:
                    pass

                window.addstr(line)
                self.cursor.inc_y()
                window.clrtoeol()
