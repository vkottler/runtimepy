"""
A module implementing a channel-environment tab HTML interface.
"""

# third-party
from vcorelib.logging import LoggerMixin
from vcorelib.math import RateLimiter

# internal
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
)
from runtimepy.mixins.markdown import MarkdownMixin
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
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
        self.set_markdown(markdown=markdown)
        super().__init__(name, app, tabs, source="env", icon=icon)

        # Logging.
        LoggerMixin.__init__(self, logger=self.command.logger)
        self.log_limiter = RateLimiter.from_s(1.0)
