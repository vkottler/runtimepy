"""
A module implementing a connection-metrics interface.
"""

# internal
from runtimepy.metrics.channel import ChannelMetrics


class ConnectionMetrics:
    """Metrics for a network connection."""

    def __init__(self) -> None:
        """Initialize this instance."""

        self.tx = ChannelMetrics()
        self.rx = ChannelMetrics()

    def update(self, other: "ConnectionMetrics") -> None:
        """Update values in this instance from values in another instance."""

        self.tx.update(other.tx)
        self.rx.update(other.rx)

    def reset(self) -> None:
        """Reset metrics."""
        self.tx.reset()
        self.rx.reset()

    def poll(self, time_ns: int = None) -> None:
        """Poll channels."""
        self.tx.poll(time_ns=time_ns)
        self.rx.poll(time_ns=time_ns)
