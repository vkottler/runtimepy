"""
A module implementing a connection-metrics structure.
"""

# third-party
from vcorelib.math import RateTracker as _RateTracker

# internal
from runtimepy.primitives import Float as _Float
from runtimepy.primitives import Uint32 as _Uint32
from runtimepy.primitives import Uint64 as _Uint64

METRICS_DEPTH = 50


class ChannelMetrics:
    """Metrics for a network channel."""

    def __init__(self) -> None:
        """Initialize this instance."""

        self.messages = _Uint32()
        self.message_rate = _Float()
        self._message_rate_tracker = _RateTracker(depth=METRICS_DEPTH)

        self.bytes = _Uint64()
        self.kbps = _Float()
        self._kbps_tracker = _RateTracker(depth=METRICS_DEPTH)

    def poll(self, time_ns: int = None) -> None:
        """Poll kbps tracking."""

        self.kbps.raw.value = self._kbps_tracker.poll(time_ns=time_ns)
        self.message_rate.raw.value = self._message_rate_tracker.poll(
            time_ns=time_ns
        )

    def increment(self, count: int, time_ns: int = None) -> None:
        """Update tracking."""

        self.messages.raw.value += 1
        self.message_rate.raw.value = self._message_rate_tracker(
            time_ns=time_ns
        )

        self.bytes.raw.value += count
        self.kbps.raw.value = self._kbps_tracker(
            time_ns=time_ns, value=float(count) / 1000.0
        )

    def reset(self) -> None:
        """Reset metrics."""

        self.messages.raw.value = 0
        self.bytes.raw.value = 0
        self.kbps.raw.value = 0.0
        self._kbps_tracker()


class ConnectionMetrics:
    """Metrics for a network connection."""

    def __init__(self) -> None:
        """Initialize this instance."""

        self.tx = ChannelMetrics()
        self.rx = ChannelMetrics()

    def reset(self) -> None:
        """Reset metrics."""
        self.tx.reset()
        self.rx.reset()

    def poll(self, time_ns: int = None) -> None:
        """Poll channels."""
        self.tx.poll(time_ns=time_ns)
        self.rx.poll(time_ns=time_ns)
