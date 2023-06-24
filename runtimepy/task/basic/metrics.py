"""
A module implementing a metrics interface for periodic tasks.
"""

# built-in
from typing import NamedTuple

# internal
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
