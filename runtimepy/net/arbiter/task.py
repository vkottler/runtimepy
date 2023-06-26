"""
A module implement a base class for arbiter periodic tasks.
"""

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.task import PeriodicTask, PeriodicTaskManager


class ArbiterTask(PeriodicTask):
    """A base class for arbiter periodic tasks."""

    def init(self, app: AppInfo) -> None:
        """Initialize this task with application information."""


class ArbiterTaskManager(PeriodicTaskManager[ArbiterTask]):
    """A task-manger class for the connection arbiter."""
