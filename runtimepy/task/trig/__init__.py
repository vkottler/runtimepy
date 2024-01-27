"""
A module implementing basic trigonometric tasks.
"""

# built-in
import math

# internal
from runtimepy.net.arbiter.task import ArbiterTask as _ArbiterTask
from runtimepy.net.arbiter.task import TaskFactory as _TaskFactory
from runtimepy.primitives import Float as _Float


class SinusoidTask(_ArbiterTask):
    """A task for logging metrics."""

    auto_finalize = True

    def _init_state(self) -> None:
        """Add channels to this instance's channel environment."""

        self.sin = _Float()
        self.cos = _Float()
        self.steps = _Float(10.0)

        self.env.channel("sin", self.sin)
        self.env.channel("cos", self.cos)
        self.env.channel("steps", self.steps, commandable=True)

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

        step = (math.tau / self.steps.value) * self.metrics.dispatches.value

        self.sin.value = math.sin(step)
        self.cos.value = math.cos(step)

        return True


class Sinusoid(_TaskFactory[SinusoidTask]):
    """A factory for the sinusoid task."""

    kind = SinusoidTask
