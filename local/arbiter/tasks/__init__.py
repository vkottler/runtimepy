"""
A module for runtimepy arbiter applications.
"""

# internal
from runtimepy.net.arbiter.task import TaskFactory

# local
from .tui import App


class TuiApp(TaskFactory[App]):
    """A TUI application factory."""

    kind = App
