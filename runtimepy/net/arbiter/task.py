"""
A module implement a base class for arbiter periodic tasks.
"""

# built-in
from typing import Generic as _Generic
from typing import TypeVar as _TypeVar

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.task import PeriodicTask, PeriodicTaskManager


class ArbiterTask(PeriodicTask):
    """A base class for arbiter periodic tasks."""

    app: AppInfo
    auto_finalize = False

    async def init(self, app: AppInfo) -> None:
        """Initialize this task with application information."""

        self.app = app


class ArbiterTaskManager(PeriodicTaskManager[ArbiterTask]):
    """A task-manger class for the connection arbiter."""


T = _TypeVar("T", bound=ArbiterTask)


class TaskFactory(_Generic[T]):
    """A task-factory base class."""

    kind: type[T]
