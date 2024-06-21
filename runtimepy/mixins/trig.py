"""
A module implementing a simple trig-channel environment mixin.
"""

# built-in
import math

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.control.env import amplitude, phase_angle, steps
from runtimepy.primitives import Float
from runtimepy.ui.controls import Controlslike


class TrigMixin:
    """A simple trig mixin class."""

    def __init__(
        self,
        env: ChannelEnvironment,
        steps_controls: Controlslike = "steps",
        amplitude_controls: Controlslike = "amplitude",
        phase_angle_controls: Controlslike = "phase",
    ) -> None:
        """Initialize this instance."""

        self.sin = Float()
        self.cos = Float()
        env.channel("sin", self.sin)
        env.channel("cos", self.cos)

        self.step_angle = float()

        self.steps = steps(env, Float, controls=steps_controls)

        self.amplitude = amplitude(env, Float, controls=amplitude_controls)

        self.sin_phase_angle = phase_angle(
            env, Float, name="sin_phase_angle", controls=phase_angle_controls
        )
        self.cos_phase_angle = phase_angle(
            env, Float, name="cos_phase_angle", controls=phase_angle_controls
        )

        def update_sin(_: float, __: float) -> None:
            """Update sin value when phase changes."""
            self._update_sin()

        def update_cos(_: float, __: float) -> None:
            """Update cos value when phase changes."""
            self._update_cos()

        # Register change callbacks.
        for prim in [self.amplitude, self.sin_phase_angle]:
            prim.register_callback(update_sin)
        for prim in [self.amplitude, self.cos_phase_angle]:
            prim.register_callback(update_cos)

    def _update_sin(self) -> None:
        """Update this instance's 'sin' member."""

        # Multiplex this on waveform shape.
        calc = math.sin(self.step_angle + self.sin_phase_angle.value)

        self.sin.value = self.amplitude.value * calc

    def _update_cos(self) -> None:
        """Update this instance's 'cos' member."""

        # Multiplex this on waveform shape.
        calc = math.cos(self.step_angle + self.cos_phase_angle.value)

        self.cos.value = self.amplitude.value * calc

    def dispatch_trig(self, step: int) -> None:
        """Dispatch trig channel updates."""

        self.step_angle = (math.tau / self.steps.value) * step
        self._update_sin()
        self._update_cos()
