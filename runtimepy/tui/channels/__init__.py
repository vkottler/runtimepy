"""
A module implementing a channel-environment user interface.
"""

# built-in
from contextlib import suppress
from typing import Optional as _Optional

# internal
from runtimepy import PKG_NAME as _PKG_NAME
from runtimepy import VERSION as _VERSION
from runtimepy.channel.environment import (
    ChannelEnvironment as _ChannelEnvironment,
)
from runtimepy.tui.mixin import CursesWindow, TuiMixin

__all__ = ["ChannelTui", "TuiMixin", "CursesWindow"]

_curses = {}  # type: ignore
with suppress(ModuleNotFoundError):
    import curses as _curses  # type: ignore


class ChannelTui(TuiMixin):
    """
    A class for implementing a text user-interface for channel environments.
    """

    def __init__(self, env: _ChannelEnvironment) -> None:
        """Initialize this text user-interface for a channel environment."""

        super().__init__()

        self._header: _Optional[CursesWindow] = None
        self._body: _Optional[CursesWindow] = None

        self.env = env
        self.channel_names: list[str] = []
        self.value_col: int = 0

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

    def init(self, window: CursesWindow) -> bool:
        """Initialize this interface's window."""

        result = super().init(window)
        if result:
            # Initialize channels for the window width and height.
            with self.env.names_pushed("ui"):
                with self.env.names_pushed("window"):
                    self.env.int_channel("width", self.cursor.max_x)
                    self.env.int_channel("height", self.cursor.max_y)

            # Collect channel names from the environment.
            self.channel_names = sorted(self.env.names)
            window = self.body

            # Initialize channel names.
            for idx, item in enumerate(self.channel_names):
                window.addstr(1 + idx, 1, item)
                self.value_col = max(self.value_col, len(item))
            self.value_col += 2

        return result

    def update_dimensions(self) -> CursesWindow:
        """Handle an update to the window's dimensions."""

        window = super().update_dimensions()

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
        header = window.subwin(header_height, self.cursor.width - 2, 2, 1)
        header.clear()
        header.box()
        self._header = header

        # Create the body box.
        body_lines = self.cursor.height - 2 - header_height - 1
        body_cols = self.cursor.width - 2
        body = window.subwin(body_lines, body_cols, 2 + header_height, 1)
        body.clear()
        body.box()
        self._body = body

    async def handle_char(self, char: int) -> bool:
        """Handle character input."""

        await super().handle_char(char)

        handled = char != -1
        if handled:
            key_str = "'" + getattr(_curses, "keyname")(char).decode() + "'"
            self.header.addstr(3, 1, f"key: {char:4} {key_str:12}")

        return handled

    async def update_header(self) -> None:
        """Update the header portion of the interface."""

        window = self.header
        window.addstr(1, 1, f"width:  {self.cursor.width:4}")
        window.addstr(2, 1, f"height: {self.cursor.height:4}")
        window.noutrefresh()

    async def update_body(self) -> None:
        """Update the body portion of the interface."""

        window = self.body

        for idx, item in enumerate(self.channel_names):
            val = self.env.value(item)

            val_str = ""
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
        self.tui_update()

        return True
