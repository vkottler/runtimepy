"""
A module implementing a structure for tracking UI state and metrics.
"""

# built-in
from typing import Optional

# internal
from runtimepy.metrics.connection import ConnectionMetrics
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.arbiter.struct import RuntimeStruct

UI: Optional["UiState"] = None


class UiState(RuntimeStruct):
    """A sample runtime structure."""

    json_metrics: ConnectionMetrics

    @staticmethod
    def singleton() -> Optional["UiState"]:
        """Attempt to get the singleton UI struct instance."""
        return UI

    async def build(self, app: AppInfo) -> None:
        """Build a struct instance's channel environment."""

        del app

        # Animation-frame time.
        self.env.float_channel("time", "double")

        # JSON-messaging interface metrics.
        self.json_metrics = ConnectionMetrics()
        with self.env.names_pushed("json"):
            self.register_connection_metrics(self.json_metrics)

        # Update singleton.
        global UI  # pylint: disable=global-statement
        UI = self
