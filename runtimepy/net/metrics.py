"""
A module implementing a connection-metrics structure.
"""

# third-party
from vcorelib.math import RateTracker

# internal
from runtimepy.primitives import Float as _Float
from runtimepy.primitives import Uint32 as _Uint32
from runtimepy.primitives import Uint64 as _Uint64


class ChannelMetrics:
    """Metrics for a network channel."""

    def __init__(self) -> None:
        """Initialize this instance."""

        self.messages = _Uint32()
        self.bytes = _Uint64()
        self.kbps = _Float()
        self._kbps_tracker = RateTracker()
        self.stale = True

    def poll(self, time_ns: int = None) -> None:
        """Poll kbps tracking."""
        self.kbps.raw.value = self._kbps_tracker.poll(time_ns=time_ns)

    def increment(self, count: int, time_ns: int = None) -> None:
        """Update tracking."""

        self.bytes.raw.value += count
        self.kbps.raw.value = self._kbps_tracker(
            time_ns=time_ns, value=float(count) / 1000.0
        )
        self.stale = False

    def reset(self) -> None:
        """Reset metrics."""

        self.messages.raw.value = 0
        self.bytes.raw.value = 0
        self.kbps.raw.value = 0.0
        self._kbps_tracker()
        self.stale = True


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
