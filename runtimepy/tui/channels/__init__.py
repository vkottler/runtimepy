"""
A module implementing a channel-environment user interface.
"""

# built-in
import curses as _curses
from typing import Optional as _Optional

# internal
from runtimepy.channel.environment import (
    ChannelEnvironment as _ChannelEnvironment,
)


class ChannelTui:
    """
    A class for implementing a text user-interface for channel environments.
    """

    def __init__(self, env: _ChannelEnvironment) -> None:
        """Initialize this text user-interface for a channel environment."""

        self._window: _Optional[_curses.window] = None

        _curses.use_default_colors()

        # Initialize channels for the window width and height.
        with env.names_pushed("ui"):
            with env.names_pushed("window"):
                self.window_width = env.int_channel("width", "uint16")[0]
                self.window_height = env.int_channel("height", "uint16")[0]

    @property
    def window(self) -> _curses.window:
        """Get this interface's window."""
        assert self._window is not None
        return self._window

    async def init(self, window: _curses.window) -> bool:
        """Initialize this interface's window."""

        assert self._window is None, "Already initialized!"
        self._window = window

        # Don't block when getting a character.
        window.nodelay(True)

        # Initialize the window dimensions.
        await self.update_dimensions()
        window.refresh()
        return True

    async def update_dimensions(self) -> None:
        """Handle an update to the window's dimensions."""

        window = self.window

        # Update width and height.
        (
            self.window_height.raw.value,
            self.window_width.raw.value,
        ) = window.getmaxyx()

        # Resize the window.
        window.resize(
            self.window_height.raw.value, self.window_width.raw.value
        )

        # Clear screen content and draw a box.
        window.clear()
        window.box()

    async def handle_char(self, char: int) -> None:
        """Handle character input."""

        if char == _curses.KEY_RESIZE:
            await self.update_dimensions()

        self.window.addstr(2, 1, str(char))

    async def dispatch(self) -> bool:
        """Dispatch this user interface."""

        window = self.window

        window.addstr(3, 1, f"width: {self.window_width.raw.value}")
        window.addstr(4, 1, f"height: {self.window_height.raw.value}")

        return True
