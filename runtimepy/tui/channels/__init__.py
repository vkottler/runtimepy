"""
A module implementing a channel-environment user interface.
"""

# built-in
import curses as _curses
from typing import Any as _Any
from typing import List as _List
from typing import Optional as _Optional

# internal
from runtimepy import PKG_NAME as _PKG_NAME
from runtimepy import VERSION as _VERSION
from runtimepy.channel.environment import (
    ChannelEnvironment as _ChannelEnvironment,
)

# Typing for something like '_curses.window' isn't supported yet.
CursesWindow = _Any


class ChannelTui:
    """
    A class for implementing a text user-interface for channel environments.
    """

    def __init__(self, env: _ChannelEnvironment) -> None:
        """Initialize this text user-interface for a channel environment."""

        self._window: _Optional[CursesWindow] = None
        self._header: _Optional[CursesWindow] = None
        self._body: _Optional[CursesWindow] = None

        # _curses.use_default_colors()
        getattr(_curses, "use_default_colors")()

        # _curses.curs_set(0)
        getattr(_curses, "curs_set")(0)

        # Initialize channels for the window width and height.
        with env.names_pushed("ui"):
            with env.names_pushed("window"):
                self.window_width = env.int_channel("width", "uint16")[0]
                self.window_height = env.int_channel("height", "uint16")[0]

        self.env = env
        self.channel_names: _List[str] = []
        self.value_col: int = 0

    @property
    def window(self) -> CursesWindow:
        """Get this interface's window."""
        assert self._window is not None
        return self._window

    @property
    def header(self) -> CursesWindow:
        """Get this interface's header window."""
        assert self._header is not None
        return self._header

    @property
    def body(self) -> CursesWindow:
        """Get this interface's body window."""
        assert self._body is not None
        return self._body

    async def init(self, window: CursesWindow) -> bool:
        """Initialize this interface's window."""

        assert self._window is None, "Already initialized!"
        self._window = window

        # Don't block when getting a character.
        window.nodelay(True)

        # Initialize the window dimensions.
        await self.update_dimensions()

        # Collect channel names from the environment.
        self.channel_names = sorted(self.env.names)
        window = self.body

        # Initialize channel names.
        for idx, item in enumerate(self.channel_names):
            window.addstr(1 + idx, 1, item)
            self.value_col = max(self.value_col, len(item))
        self.value_col += 2

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
        window.addstr(
            1,
            1,
            f"Channel Environment User Interface ({_PKG_NAME}-{_VERSION})",
        )

        # Create the header box.
        header_height = 5
        header = window.subwin(
            header_height, self.window_width.raw.value - 2, 2, 1
        )
        header.clear()
        header.box()
        self._header = header

        # Create the body box.
        body_lines = self.window_height.raw.value - 2 - header_height - 1
        body_cols = self.window_width.raw.value - 2
        body = window.subwin(body_lines, body_cols, 2 + header_height, 1)
        body.clear()
        body.box()
        self._body = body

    async def handle_char(self, char: int) -> None:
        """
        Handle character input.
        """

        if char != -1:
            if char == getattr(_curses, "KEY_RESIZE"):
                await self.update_dimensions()

            key_str = "'" + getattr(_curses, "keyname")(char).decode() + "'"

            self.header.addstr(3, 1, f"key: {char:4} {key_str:12}")

    async def update_header(self) -> None:
        """Update the header portion of the interface."""

        window = self.header
        window.addstr(1, 1, f"width:  {self.window_width.raw.value:4}")
        window.addstr(2, 1, f"height: {self.window_height.raw.value:4}")
        window.noutrefresh()

    async def update_body(self) -> None:
        """Update the body portion of the interface."""

        window = self.body

        for idx, item in enumerate(self.channel_names):
            val = self.env.value(item)

            if isinstance(val, float):
                val_str = f"{val:5.6f}"
            elif isinstance(val, int):
                val_str = f"{val:<5d}"

            window.addstr(1 + idx, self.value_col, val_str)

        window.noutrefresh()

    async def dispatch(self) -> bool:
        """Dispatch this user interface."""

        # Update window states.
        await self.update_header()
        await self.update_body()

        # Re-draw the screen.
        getattr(_curses, "doupdate")()
        return True
