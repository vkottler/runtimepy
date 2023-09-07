"""
A module implementing a basic TUI application.
"""

# built-in
from typing import Dict

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.net.arbiter import AppInfo
from runtimepy.tui.mixin import CursesWindow

# local
from .base import AppBase


class App(AppBase):
    """A simple TUI application."""

    envs: Dict[str, ChannelEnvironment]

    async def init(self, app: AppInfo) -> None:
        """Initialize this task with application information."""

        await super().init(app)

        self.envs: Dict[str, ChannelEnvironment] = {"self": self.env}

        for name, conn in self.app.connections.items():
            self.envs[name] = conn.env

    def draw(self, window: CursesWindow) -> None:
        """Draw the application."""

        self.cursor.reset()

        for env_name, env in self.envs.items():
            window.addstr(f"========== {env_name} ==========")
            window.clrtoeol()
            if not self.cursor.inc_y():
                break

            for name in env.names:
                line = name

                chan, enum = env[name]

                # do floats better
                line += " " + str(chan)

                if enum is not None:
                    pass

                window.addstr(line)
                window.clrtoeol()
                if not self.cursor.inc_y():
                    break
