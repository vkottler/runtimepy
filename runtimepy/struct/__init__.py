"""
A module implementing a runtime structure base.
"""

# built-in
from logging import getLogger as _getLogger

# third-party
from vcorelib.io.types import JsonObject as _JsonObject

# internal
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
)
from runtimepy.mixins.environment import ChannelEnvironmentMixin
from runtimepy.mixins.logging import LoggerMixinLevelControl
from runtimepy.mixins.markdown import MarkdownMixin


class RuntimeStructBase(
    LoggerMixinLevelControl, ChannelEnvironmentMixin, MarkdownMixin
):
    """A base runtime structure."""

    log_level_channel: bool = True

    # Unclear why this is/was necessary (mypy bug?)
    markdown: str

    def __init__(self, name: str, config: _JsonObject) -> None:
        """Initialize this instance."""

        self.name = name
        self.set_markdown(config=config)
        LoggerMixinLevelControl.__init__(self, logger=_getLogger(self.name))
        ChannelEnvironmentMixin.__init__(self)
        if self.log_level_channel:
            self.setup_level_channel(self.env)
        self.command = ChannelCommandProcessor(self.env, self.logger)
        self.config = config

    def poll(self) -> None:
        """
        A method that other runtime entities can call to perform canonical
        updates to this struct's environment.
        """


StructMap = dict[str, RuntimeStructBase]
