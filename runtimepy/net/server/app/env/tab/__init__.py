"""
A module implementing a channel-environment tab HTML interface.
"""

# internal
from runtimepy.net.server.app.env.tab.html import ChannelEnvironmentTabHtml
from runtimepy.net.server.app.env.tab.message import (
    ChannelEnvironmentTabMessaging,
)


class ChannelEnvironmentTab(
    ChannelEnvironmentTabMessaging, ChannelEnvironmentTabHtml
):
    """A class aggregating all channel-environment tab interfaces."""

    all_tabs: dict[str, "ChannelEnvironmentTab"] = {}

    def init(self) -> None:
        """Initialize this instance."""

        super().init()

        # Update global mapping.
        type(self).all_tabs[self.name] = self
