"""
A module implementing a channel-environment class mixin.
"""

# internal
from runtimepy import METRICS_NAME
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.metrics import ConnectionMetrics, PeriodicTaskMetrics


class ChannelEnvironmentMixin:
    """A simple channel-environment mixin."""

    env: ChannelEnvironment

    def __init__(self, env: ChannelEnvironment = None, **kwargs) -> None:
        """Initialize this instance."""

        if not hasattr(self, "env"):
            if env is None:
                env = ChannelEnvironment(**kwargs)
            self.env = env

    def register_task_metrics(
        self, metrics: PeriodicTaskMetrics, namespace: str = METRICS_NAME
    ) -> None:
        """Register periodic task metrics."""

        with self.env.names_pushed(namespace):
            self.env.channel(
                "dispatches",
                metrics.dispatches,
                description="Dispatch call counter for this task.",
            )
            self.env.channel(
                "rate_hz",
                metrics.rate_hz,
                description="Measured dispatch rate in Hertz.",
            )
            self.env.channel(
                "average_s",
                metrics.average_s,
                description="An averaged dispatch time measurement.",
            )
            self.env.channel(
                "max_s",
                metrics.max_s,
                description="Maximum dispatch time measured.",
            )
            self.env.channel(
                "min_s",
                metrics.min_s,
                description="Minimum dispatch time measured.",
            )
            self.env.channel(
                "overruns",
                metrics.overruns,
                description="Dispatch time exceeding period counter.",
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
                with self.env.names_pushed(name):
                    self.env.channel(
                        "messages",
                        direction.messages,
                        description=f"Number of messages {verb}.",
                    )
                    self.env.channel(
                        "messages_rate",
                        direction.message_rate,
                        description=f"Messages per second {verb}.",
                    )
                    self.env.channel(
                        "bytes",
                        direction.bytes,
                        description=f"Number of bytes {verb}.",
                    )
                    self.env.channel(
                        "kbps",
                        direction.kbps,
                        description=f"Kilobits per second {verb}.",
                    )
