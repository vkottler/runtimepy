"""
A module implementing basic trigonometric tasks.
"""

# internal
from runtimepy.mixins.trig import TrigMixin
from runtimepy.net.arbiter.task import ArbiterTask as _ArbiterTask
from runtimepy.net.arbiter.task import TaskFactory as _TaskFactory


class SinusoidTask(_ArbiterTask, TrigMixin):
    """A task for logging metrics."""

    auto_finalize = True

    def _init_state(self) -> None:
        """Add channels to this instance's channel environment."""
        TrigMixin.__init__(self, self.env)

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""
        self.dispatch_trig(self.metrics.dispatches.value)
        return True


class Sinusoid(_TaskFactory[SinusoidTask]):
    """A factory for the sinusoid task."""

    kind = SinusoidTask
