"""
A module implementing a structure for tracking UI state and metrics.
"""

# built-in
from typing import Optional

# internal
from runtimepy.metrics.connection import ConnectionMetrics
from runtimepy.mixins.psutil import PsutilMixin
from runtimepy.net.arbiter.info import RuntimeStruct
from runtimepy.primitives import Float

UI: Optional["UiState"] = None


class UiState(RuntimeStruct, PsutilMixin):
    """A sample runtime structure."""

    json_metrics: ConnectionMetrics

    time_ms: Float
    frame_period_ms: Float

    use_psutil: bool

    @staticmethod
    def singleton() -> Optional["UiState"]:
        """Attempt to get the singleton UI struct instance."""
        return UI

    def init_env(self) -> None:
        """Initialize this sample environment."""

        # Animation-frame time.
        self.time_ms = Float()
        self.env.float_channel("time_ms", self.time_ms)
        self.frame_period_ms = Float()
        self.env.float_channel("frame_period_ms", self.frame_period_ms)

        # Number of concurrent connections.
        self.env.int_channel("num_connections", "uint8")

        # JSON-messaging interface metrics.
        self.json_metrics = ConnectionMetrics()
        self.register_connection_metrics(self.json_metrics, "json")

        # System metrics.
        self.use_psutil = self.config.get("psutil", True)  # type: ignore
        if self.use_psutil:
            self.init_psutil(self.env)

        # Update singleton.
        global UI  # pylint: disable=global-statement
        UI = self

    def poll(self) -> None:
        """
        A method that other runtime entities can call to perform canonical
        updates to this struct's environment.
        """

        if self.use_psutil:
            self.poll_psutil(self.frame_period_ms.value)
