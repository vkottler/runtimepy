"""
    A module implementing basic trigonometric tasks.
"""

# internal
from runtimepy.net.arbiter.task import ArbiterTask as _ArbiterTask
from runtimepy.net.arbiter.task import TaskFactory as _TaskFactory


class SinusoidTask(_ArbiterTask):
    """A task for logging metrics."""

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

        return True


class Sinusoid(_TaskFactory[SinusoidTask]):
    """A factory for the sinusoid task."""

    kind = SinusoidTask
