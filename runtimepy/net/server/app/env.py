"""
A module implementing a channel-environment tab HTML interface.
"""

# third-party
from svgen.element import Element

# internal
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
)
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server.app.bootstrap import icon_str
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.elements import div
from runtimepy.net.server.app.tab import Tab


class ChannelEnvironmentTab(Tab):
    """A channel-environment tab interface."""

    def __init__(
        self,
        name: str,
        command: ChannelCommandProcessor,
        app: AppInfo,
        tabs: TabbedContent,
        icon: str = "alarm",
    ) -> None:
        """Initialize this instance."""

        self.command = command
        super().__init__(name, app, tabs, source="env")

        # Use an icon as the start of the button.
        self.button.text = icon_str(icon) + " " + self.name

    def compose(self, parent: Element) -> None:
        """Compose the tab's HTML elements."""

        for name in self.command.env.names:
            div(text=name, parent=parent)
