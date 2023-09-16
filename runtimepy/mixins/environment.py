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

        if env is None:
            env = ChannelEnvironment(**kwargs)
        self.env = env

    def register_task_metrics(
        self, metrics: PeriodicTaskMetrics, namespace: str = METRICS_NAME
    ) -> None:
        """Register periodic task metrics."""

        with self.env.names_pushed(namespace):
            self.env.channel("dispatches", metrics.dispatches)
            self.env.channel("rate_hz", metrics.rate_hz)
            self.env.channel("average_s", metrics.average_s)
            self.env.channel("max_s", metrics.max_s)
            self.env.channel("min_s", metrics.min_s)
            self.env.channel("overruns", metrics.overruns)

    def register_connection_metrics(
        self, metrics: ConnectionMetrics, namespace: str = METRICS_NAME
    ) -> None:
        """Register connection metrics."""

        with self.env.names_pushed(namespace):
            for name, direction in [("tx", metrics.tx), ("rx", metrics.rx)]:
                with self.env.names_pushed(name):
                    self.env.channel("messages", direction.messages)
                    self.env.channel("messages_rate", direction.message_rate)
                    self.env.channel("bytes", direction.bytes)
                    self.env.channel("kbps", direction.kbps)
