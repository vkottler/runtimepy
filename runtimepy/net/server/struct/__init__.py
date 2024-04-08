"""
A module implementing a structure for tracking UI state and metrics.
"""

# built-in
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.arbiter.struct import RuntimeStruct


class UiState(RuntimeStruct):
    """A sample runtime structure."""

    async def build(self, app: AppInfo) -> None:
        """Build a struct instance's channel environment."""

        del app

        # Animation-frame time.
        self.env.float_channel("time", "double")
