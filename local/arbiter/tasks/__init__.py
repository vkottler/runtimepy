"""
A module for runtimepy arbiter applications.
"""

# internal
from runtimepy.net.arbiter.task import TaskFactory

# local
from .tui import Tui


class TuiApp(TaskFactory[Tui]):
    """A TUI application factory."""

    kind = Tui
