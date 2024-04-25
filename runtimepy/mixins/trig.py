"""
A module implementing a simple trig-channel environment mixin.
"""

# built-in
import math

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.primitives import Float as _Float


class TrigMixin:
    """A simple trig mixin class."""

    def __init__(self, env: ChannelEnvironment) -> None:
        """Initialize this instance."""

        self.sin = _Float()
        self.cos = _Float()
        self.steps = _Float(10.0)

        env.channel("sin", self.sin)
        env.channel("cos", self.cos)
        env.channel("steps", self.steps, commandable=True)

    def dispatch_trig(self, step: int) -> None:
        """Dispatch trig channel updates."""
        step_angle = (math.tau / self.steps.value) * step
        self.sin.value = math.sin(step_angle)
        self.cos.value = math.cos(step_angle)
