"""
A module implementing interfaces for psutil.
"""

# third-party
import psutil
from vcorelib.math import WeightedAverage, metrics_time_ns

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.primitives import Float


class PsutilMixin:
    """A simple psutil runtime interface."""

    process: psutil.Process
    cpu_average: WeightedAverage

    memory_percent: Float
    cpu_percent: Float

    def init_psutil(self, env: ChannelEnvironment) -> None:
        """Initialize psutil-based metrics."""

        # System metrics.
        self.process = psutil.Process()
        self.cpu_average = WeightedAverage(depth=60)
        self.memory_percent = Float(time_source=metrics_time_ns)
        self.cpu_percent = Float(time_source=metrics_time_ns)

        env.float_channel("memory_percent", self.memory_percent)
        env.float_channel("cpu_percent", self.cpu_percent)

    def poll_psutil(self, weight: float) -> None:
        """Poll psutil-based metrics."""

        self.memory_percent.value = psutil.virtual_memory().percent

        with self.process.oneshot():
            self.cpu_average(
                self.process.cpu_percent(),
                weight=weight,
            )
            self.cpu_percent.value = self.cpu_average.average()
