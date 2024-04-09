"""
A module implementing a structure for tracking UI state and metrics.
"""

# built-in
from typing import Optional

# third-party
import psutil
from vcorelib.math import WeightedAverage

# internal
from runtimepy.metrics.connection import ConnectionMetrics
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.arbiter.struct import RuntimeStruct
from runtimepy.primitives import Float

UI: Optional["UiState"] = None


class UiState(RuntimeStruct):
    """A sample runtime structure."""

    json_metrics: ConnectionMetrics
    process: psutil.Process
    cpu_average: WeightedAverage

    time_ms: Float
    frame_period_ms: Float
    memory_percent: Float
    cpu_percent: Float

    @staticmethod
    def singleton() -> Optional["UiState"]:
        """Attempt to get the singleton UI struct instance."""
        return UI

    async def build(self, app: AppInfo) -> None:
        """Build a struct instance's channel environment."""

        del app

        # Animation-frame time.
        self.time_ms = Float()
        self.env.float_channel("time_ms", self.time_ms)
        self.frame_period_ms = Float()
        self.env.float_channel("frame_period_ms", self.frame_period_ms)

        # Number of concurrent connections.
        self.env.int_channel("num_connections", "uint8")

        # JSON-messaging interface metrics.
        self.json_metrics = ConnectionMetrics()
        with self.env.names_pushed("json"):
            self.register_connection_metrics(self.json_metrics)

        # System metrics.
        self.process = psutil.Process()
        self.cpu_average = WeightedAverage(depth=60)
        self.memory_percent = Float()
        self.env.float_channel("memory_percent", self.memory_percent)
        self.cpu_percent = Float()
        self.env.float_channel("cpu_percent", self.cpu_percent)

        # Update singleton.
        global UI  # pylint: disable=global-statement
        UI = self

    def poll(self) -> None:
        """
        A method that other runtime entities can call to perform canonical
        updates to this struct's environment.
        """

        self.memory_percent.value = psutil.virtual_memory().percent

        with self.process.oneshot():
            self.cpu_average(
                self.process.cpu_percent(),
                weight=self.frame_period_ms.value,
            )
            self.cpu_percent.value = self.cpu_average.average()
