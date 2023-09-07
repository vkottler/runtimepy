"""
A module implementing a channel-metrics interface.
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

    def __str__(self) -> str:
        """Get metrics as a string."""

        return "\t".join(
            [
                f"messages={self.messages.value}",
                f"message_rate={self.message_rate.value:.2f}",
                f"bytes={self.bytes.value}",
                f"kbps={self.kbps.value:.2f}",
            ]
        )

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

        # Multiply by 8 to get bits from bytes.
        self.kbps.raw.value = (
            self._kbps_tracker(time_ns=time_ns, value=float(count) / 1000.0)
            * 8
        )

    def reset(self) -> None:
        """Reset metrics."""

        self.messages.raw.value = 0
        self.bytes.raw.value = 0
        self.kbps.raw.value = 0.0
        self._kbps_tracker.reset()
