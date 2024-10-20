"""
A module implementing a channel-environment tab HTML interface.
"""

# third-party
from vcorelib.io import MarkdownMixin
from vcorelib.logging import LoggerMixin
from vcorelib.math import RateLimiter

# internal
from runtimepy import PKG_NAME
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
)
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.html.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.tab import Tab


class ChannelEnvironmentTabBase(Tab, LoggerMixin, MarkdownMixin):
    """A channel-environment tab interface."""

    def __init__(
        self,
        name: str,
        command: ChannelCommandProcessor,
        app: AppInfo,
        tabs: TabbedContent,
        icon: str = "alarm",
        markdown: str = None,
    ) -> None:
        """Initialize this instance."""

        self.command = command
        self.set_markdown(markdown=markdown, package=PKG_NAME)
        super().__init__(name, app, tabs, source="env", icon=icon)

        # Logging.
        LoggerMixin.__init__(self, logger=self.command.logger)
        self.log_limiter = RateLimiter.from_s(1.0)
