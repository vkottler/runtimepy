"""
A module implementing a channel-metrics interface.
"""

# third-party
from vcorelib.math import RateTracker as _RateTracker
from vcorelib.math import metrics_time_ns as _metrics_time_ns

# internal
from runtimepy.primitives import Float as _Float
from runtimepy.primitives import Uint32 as _Uint32
from runtimepy.primitives import Uint64 as _Uint64

METRICS_DEPTH = 50


class ChannelMetrics:
    """Metrics for a network channel."""

    def __init__(self) -> None:
        """Initialize this instance."""

        self.messages = _Uint32(time_source=_metrics_time_ns)
        self.message_rate = _Float(time_source=_metrics_time_ns)
        self._message_rate_tracker = _RateTracker(
            depth=METRICS_DEPTH, source=_metrics_time_ns
        )

        self.bytes = _Uint64(time_source=_metrics_time_ns)
        self.kbps = _Float(time_source=_metrics_time_ns)
        self._kbps_tracker = _RateTracker(
            depth=METRICS_DEPTH, source=_metrics_time_ns
        )

    def update(self, other: "ChannelMetrics") -> None:
        """Update values in this instance from values in another instance."""

        self.messages.value = other.messages.value
        self.message_rate.value = other.message_rate.value
        self.bytes.value = other.bytes.value
        self.kbps.value = other.kbps.value

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

        self.kbps.value = self._kbps_tracker.poll(time_ns=time_ns)
        self.message_rate.value = self._message_rate_tracker.poll(
            time_ns=time_ns
        )

    def increment(self, count: int, time_ns: int = None) -> None:
        """Update tracking."""

        self.messages.value += 1
        self.message_rate.value = self._message_rate_tracker(time_ns=time_ns)

        self.bytes.value += count

        # Multiply by 8 to get bits from bytes.
        self.kbps.value = (
            self._kbps_tracker(time_ns=time_ns, value=float(count) / 1000.0)
            * 8
        )

    def reset(self) -> None:
        """Reset metrics."""

        self.messages.value = 0
        self.bytes.value = 0
        self.kbps.value = 0.0
        self._kbps_tracker.reset()
