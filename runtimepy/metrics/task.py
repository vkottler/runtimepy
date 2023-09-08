"""
A module implementing a periodic-task metrics interface.
"""

# built-in
from asyncio import AbstractEventLoop
from contextlib import contextmanager
from typing import Iterator, NamedTuple

# third-party
from vcorelib.math import MovingAverage, RateTracker

# internal
from runtimepy.primitives import Double as _Double
from runtimepy.primitives import Float as _Float
from runtimepy.primitives import Uint32 as _Uint32


class PeriodicTaskMetrics(NamedTuple):
    """Metrics for a periodic tasks."""

    dispatches: _Uint32
    rate_hz: _Float
    average_s: _Float
    max_s: _Float
    min_s: _Float

    @staticmethod
    def create() -> "PeriodicTaskMetrics":
        """Create a new metrics instance."""

        return PeriodicTaskMetrics(
            _Uint32(), _Float(), _Float(), _Float(), _Float()
        )

    @contextmanager
    def measure(
        self,
        eloop: AbstractEventLoop,
        rate: RateTracker,
        dispatch: MovingAverage,
        iter_time: _Double,
    ) -> Iterator[None]:
        """Measure the time spent yielding and update data."""

        start = eloop.time()
        self.rate_hz.raw.value = rate(int(start * 1e9))

        yield

        iter_time.value = eloop.time() - start

        # Update runtime metrics.
        self.dispatches.raw.value += 1
        self.average_s.raw.value = dispatch(iter_time.value)
        self.max_s.raw.value = dispatch.max
        self.min_s.raw.value = dispatch.min
