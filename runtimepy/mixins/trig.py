"""
A module implementing a simple trig-channel environment mixin.
"""

# built-in
import math

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.primitives import Float as _Float
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

        self.sin = _Float()
        self.cos = _Float()
        self.steps = _Float()

        self.step_angle = float()

        env.channel("sin", self.sin)
        env.channel("cos", self.cos)

        env.channel(
            "steps",
            self.steps,
            commandable=True,
            controls=steps_controls,
        )

        self.amplitude = _Float()
        env.channel(
            "amplitude",
            self.amplitude,
            commandable=True,
            controls=amplitude_controls,
        )

        self.sin_phase_angle = _Float()
        self.cos_phase_angle = _Float()

        env.channel(
            "sin_phase_angle",
            self.sin_phase_angle,
            commandable=True,
            controls=phase_angle_controls,
        )

        env.channel(
            "cos_phase_angle",
            self.cos_phase_angle,
            commandable=True,
            controls=phase_angle_controls,
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
