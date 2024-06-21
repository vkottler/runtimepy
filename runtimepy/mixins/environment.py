"""
A module implementing a channel-environment class mixin.
"""

# internal
from runtimepy import METRICS_NAME
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.metrics import ConnectionMetrics, PeriodicTaskMetrics
from runtimepy.metrics.channel import ChannelMetrics

# 10 Hz metrics.
METRICS_MIN_PERIOD_S = 0.1


class ChannelEnvironmentMixin:
    """A simple channel-environment mixin."""

    env: ChannelEnvironment

    def __init__(self, env: ChannelEnvironment = None, **kwargs) -> None:
        """Initialize this instance."""

        if not hasattr(self, "env"):
            if env is None:
                env = ChannelEnvironment(**kwargs)
            self.env = env

    def __hash__(self) -> int:
        """Get a hash for this instance."""
        return id(self.env)

    def register_task_metrics(
        self, metrics: PeriodicTaskMetrics, namespace: str = METRICS_NAME
    ) -> None:
        """Register periodic task metrics."""

        with self.env.names_pushed(namespace):
            self.env.channel(
                "dispatches",
                metrics.dispatches,
                description="Dispatch call counter for this task.",
                min_period_s=METRICS_MIN_PERIOD_S,
            )
            self.env.channel(
                "rate_hz",
                metrics.rate_hz,
                description="Measured dispatch rate in Hertz.",
                min_period_s=METRICS_MIN_PERIOD_S,
            )
            self.env.channel(
                "average_s",
                metrics.average_s,
                description="An averaged dispatch time measurement.",
                min_period_s=METRICS_MIN_PERIOD_S,
            )
            self.env.channel(
                "max_s",
                metrics.max_s,
                description="Maximum dispatch time measured.",
                min_period_s=METRICS_MIN_PERIOD_S,
            )
            self.env.channel(
                "min_s",
                metrics.min_s,
                description="Minimum dispatch time measured.",
                min_period_s=METRICS_MIN_PERIOD_S,
            )
            self.env.channel(
                "overruns",
                metrics.overruns,
                description="Dispatch time exceeding period counter.",
                min_period_s=METRICS_MIN_PERIOD_S,
            )

    def register_channel_metrics(
        self, name: str, channel: ChannelMetrics, verb: str
    ) -> None:
        """Register individual channel metrics."""

        with self.env.names_pushed(name):
            self.env.channel(
                "messages",
                channel.messages,
                description=f"Number of messages {verb}.",
                min_period_s=METRICS_MIN_PERIOD_S,
            )
            self.env.channel(
                "messages_rate",
                channel.message_rate,
                description=f"Messages per second {verb}.",
                min_period_s=METRICS_MIN_PERIOD_S,
            )
            self.env.channel(
                "bytes",
                channel.bytes,
                description=f"Number of bytes {verb}.",
                min_period_s=METRICS_MIN_PERIOD_S,
            )
            self.env.channel(
                "kbps",
                channel.kbps,
                description=f"Kilobits per second {verb}.",
                min_period_s=METRICS_MIN_PERIOD_S,
            )

    def register_connection_metrics(
        self, metrics: ConnectionMetrics, namespace: str = METRICS_NAME
    ) -> None:
        """Register connection metrics."""

        with self.env.names_pushed(namespace):
            for name, direction, verb in [
                ("tx", metrics.tx, "transmitted"),
                ("rx", metrics.rx, "received"),
            ]:
                self.register_channel_metrics(name, direction, verb)
