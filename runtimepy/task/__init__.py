"""
A module implementing an asynchronous task interface.
"""

# built-in
import asyncio as _asyncio
from logging import getLogger as _getLogger

# third-party
from vcorelib.logging import LoggerMixin as _LoggerMixin
from vcorelib.math.analysis.average import MovingAverage as _MovingAverage
from vcorelib.math.analysis.rate import RateTracker as _RateTracker

# internal
from runtimepy.channel.environment import (
    ChannelEnvironment as _ChannelEnvironment,
)


class AsyncTask(_LoggerMixin):
    """A basic implementation of a periodic task."""

    def __init__(
        self,
        name: str,
        period_s: float,
        env: _ChannelEnvironment,
        average_depth: int = 10,
        max_iterations: int = 0,
    ) -> None:
        """Initialize this asynchronous task."""

        super().__init__(logger=_getLogger(name))

        self.name = name
        self.dispatch_rate = _RateTracker(depth=average_depth)
        self.dispatch_time = _MovingAverage(depth=average_depth)

        with env.names_pushed(name):
            # Track whether or not this task is currently enabled.
            self.enabled = env.bool_channel("enabled", commandable=True)[0]

            # Keep track of the time between task iterations in seconds.
            self.period_s = env.float_channel("period_s", commandable=True)
            self.period_s.raw.value = period_s

            # Allow commanding a maximum number of iterations.
            self.max_iterations = env.int_channel(
                "max_iterations", commandable=True
            )[0]
            self.max_iterations.raw.value = max_iterations

            with env.names_pushed("metrics"):
                # Track the number of times this task has been dispatched.
                self.dispatches = env.int_channel("dispatches", kind="uint8")[
                    0
                ]

                # Track metrics for how long this task takes to execute.
                self.rate_hz = env.float_channel("rate_hz")
                self.average_s = env.float_channel("average_s")
                self.max_s = env.float_channel("max_s")
                self.min_s = env.float_channel("min_s")

            # Initialize task-specific channels.
            self.init_channels(env)

        self.env = env

    def init_channels(self, env: _ChannelEnvironment) -> None:
        """Initialize task-specific channels."""

    async def init(self, *_, **__) -> bool:
        """Initialize this task."""
        return True

    async def dispatch(self, *_, **__) -> bool:
        """Dispatch this task."""
        return True

    def reset_metrics(self) -> None:
        """Reset metrics channel values."""

        self.dispatch_rate.reset()
        self.dispatch_time.reset()
        self.dispatches.raw.value = 0
        self.rate_hz.raw.value = 0.0
        self.average_s.raw.value = 0.0
        self.max_s.raw.value = 0.0
        self.min_s.raw.value = 0.0

    def log_metrics(self) -> None:
        """Log information related to metrics channels."""

        self.logger.info(
            "'%s' dispatches: %d.", self.name, self.dispatches.raw.value
        )
        self.logger.info(
            "'%s' rate: %0.6f Hz.", self.name, self.rate_hz.raw.value
        )
        self.logger.info(
            "'%s' average time: %0.6fs.", self.name, self.average_s.raw.value
        )
        self.logger.info(
            "'%s' max time: %0.6fs.", self.name, self.max_s.raw.value
        )
        self.logger.info(
            "'%s' min time: %0.6fs.", self.name, self.min_s.raw.value
        )

    @property
    def rate_str(self) -> str:
        """Get this periodic's rate as a string."""
        return f"{1.0 / self.period_s.raw.value:0.3f} Hz"

    def enable(self) -> None:
        """Enable this task."""
        self.enabled.raw.value = True

    def disable(self) -> None:
        """Disable this task."""
        self.enabled.raw.value = False

    async def run(self, *args, **kwargs) -> None:
        """Run this task while it's enabled."""

        eloop = _asyncio.get_running_loop()

        self.logger.info("Starting task '%s' at %s.", self.name, self.rate_str)

        self.reset_metrics()

        # Always re-enable the task if this is called.
        self.enable()

        # Run this task's initialization.
        self.enabled.raw.value &= await _asyncio.shield(
            self.init(*args, **kwargs)
        )

        while self.enabled:
            # Keep track of the rate that this task is running at.
            start = eloop.time()
            self.rate_hz.raw.value = self.dispatch_rate(int(start * 1e9))

            self.enabled.raw.value &= await _asyncio.shield(
                self.dispatch(*args, **kwargs)
            )
            exec_time = eloop.time() - start

            # Update runtime metrics.
            self.dispatches.raw.value += 1
            self.average_s.raw.value = self.dispatch_time(exec_time)
            self.max_s.raw.value = self.dispatch_time.max
            self.min_s.raw.value = self.dispatch_time.min

            # Check if we've performed the maximum specified number of
            # dispatches.
            if (
                self.max_iterations.raw.value > 0
                and self.dispatches.raw.value >= self.max_iterations.raw.value
            ):
                self.disable()

            if self.enabled:
                try:
                    await _asyncio.sleep(
                        max(self.period_s.raw.value - exec_time, 0)
                    )
                except _asyncio.CancelledError:
                    self.logger.warning("Task '%s' was cancelled!", self.name)
                    self.disable()

        self.logger.info("Task '%s' stopped.", self.name)
        self.log_metrics()
