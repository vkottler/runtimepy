"""
A task entry-point for a text user-interface.
"""

# internal
from runtimepy.channel.environment import (
    ChannelEnvironment as _ChannelEnvironment,
)
from runtimepy.task import AsyncTask as _AsyncTask
from runtimepy.tui.channels import ChannelTui as _ChannelTui
from runtimepy.tui.channels import CursesWindow as _CursesWindow


class TuiTask(_AsyncTask):
    """A task implementation for a text user-interface."""

    def init_channels(self, env: _ChannelEnvironment) -> None:
        """Initialize task-specific channels."""

        # Create the user interface.
        self.tui = _ChannelTui(env)

    async def init(self, *args, **__) -> bool:
        """Initialize this task."""

        # Initialize the interface.
        window: _CursesWindow = args[0]
        return await self.tui.init(window)

    async def dispatch(self, *_, **__) -> bool:
        """Dispatch this task."""

        window = self.tui.window

        # Check if we have input waiting.
        await self.tui.handle_char(window.getch())

        # Dispatch the interface.
        return await self.tui.dispatch()
