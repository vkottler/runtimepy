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
    ) -> None:
        """Initialize this asynchronous task."""

        super().__init__(logger=_getLogger(name))

        self.name = name
        self.dispatch_rate = _RateTracker(depth=average_depth)
        self.dispatch_time = _MovingAverage(depth=average_depth)

        with env.names_pushed(name):
            # Track whether or not this task is currently enabled.
            self.enabled = env.bool_channel("enabled", commandable=True)[0]
            self.enabled.raw.value = True

            # Keep track of the time between task iterations in seconds.
            self.period_s = env.float_channel("period_s", commandable=True)
            self.period_s.raw.value = period_s

            # Track the number of times this task has been dispatched.
            self.dispatches = env.int_channel("dispatches", kind="uint8")[0]

            # Track metrics for how long this task takes to execute.
            self.rate_hz = env.float_channel("rate_hz")
            self.average_s = env.float_channel("average_s")
            self.max_s = env.float_channel("max_s")
            self.min_s = env.float_channel("min_s")

    async def dispatch(self) -> bool:
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

    async def run(self) -> None:
        """Run this task while it's enabled."""

        eloop = _asyncio.get_running_loop()

        self.logger.info("Starting task '%s' at %s.", self.name, self.rate_str)

        self.reset_metrics()

        while self.enabled:
            # Keep track of the rate that this task is running at.
            start = eloop.time()
            self.rate_hz.raw.value = self.dispatch_rate(int(start * 1e9))

            self.enabled.raw.value &= await _asyncio.shield(self.dispatch())
            exec_time = eloop.time() - start

            # Update runtime metrics.
            self.dispatches.raw.value += 1
            self.average_s.raw.value = self.dispatch_time(exec_time)
            self.max_s.raw.value = self.dispatch_time.max
            self.min_s.raw.value = self.dispatch_time.min

            if self.enabled:
                try:
                    await _asyncio.sleep(
                        max(self.period_s.raw.value - exec_time, 0)
                    )
                except _asyncio.CancelledError:
                    self.enabled.raw.value = False

        self.logger.info("Task '%s' stopped.", self.name)
        self.log_metrics()
