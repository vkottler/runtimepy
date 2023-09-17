"""
A module implementing a periodic-task metrics interface.
"""

# built-in
from asyncio import AbstractEventLoop
from contextlib import contextmanager
from typing import Iterator, NamedTuple

# third-party
from vcorelib.math import MovingAverage, RateTracker, to_nanos

# internal
from runtimepy.primitives import Double as _Double
from runtimepy.primitives import Float as _Float
from runtimepy.primitives import Uint16 as _Uint16
from runtimepy.primitives import Uint32 as _Uint32


class PeriodicTaskMetrics(NamedTuple):
    """Metrics for a periodic tasks."""

    dispatches: _Uint32
    rate_hz: _Float
    average_s: _Float
    max_s: _Float
    min_s: _Float
    overruns: _Uint16

    @staticmethod
    def create() -> "PeriodicTaskMetrics":
        """Create a new metrics instance."""

        return PeriodicTaskMetrics(
            _Uint32(), _Float(), _Float(), _Float(), _Float(), _Uint16()
        )

    @contextmanager
    def measure(
        self,
        eloop: AbstractEventLoop,
        rate: RateTracker,
        dispatch: MovingAverage,
        iter_time: _Double,
        period_s: float,
    ) -> Iterator[None]:
        """Measure the time spent yielding and update data."""

        start = eloop.time()
        self.rate_hz.value = rate(to_nanos(start))

        yield

        iter_time.value = eloop.time() - start

        # Update runtime metrics.
        self.dispatches.value += 1
        self.average_s.value = dispatch(iter_time.value)
        self.max_s.value = dispatch.max
        self.min_s.value = dispatch.min
        if iter_time.value > period_s:
            self.overruns.value += 1
