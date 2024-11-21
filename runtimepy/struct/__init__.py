"""
A module implementing a runtime structure base.
"""

# built-in
from argparse import Namespace
import asyncio
from logging import getLogger as _getLogger
from typing import Optional

# third-party
from vcorelib.io.markdown import MarkdownMixin
from vcorelib.io.types import JsonObject as _JsonObject

# internal
from runtimepy import PKG_NAME
from runtimepy.channel.environment.command import FieldOrChannel
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
)
from runtimepy.mixins.async_command import AsyncCommandProcessingMixin
from runtimepy.mixins.environment import ChannelEnvironmentMixin
from runtimepy.mixins.logging import LoggerMixinLevelControl


class RuntimeStructBase(
    LoggerMixinLevelControl,
    ChannelEnvironmentMixin,
    AsyncCommandProcessingMixin,
    MarkdownMixin,
):
    """A base runtime structure."""

    log_level_channel: bool = True

    # Unclear why this is/was necessary (mypy bug?)
    markdown: str

    def __init__(
        self, name: str, config: _JsonObject, markdown: str = None
    ) -> None:
        """Initialize this instance."""

        self.name = name
        self.set_markdown(config=config, markdown=markdown, package=PKG_NAME)
        LoggerMixinLevelControl.__init__(self, logger=_getLogger(self.name))
        ChannelEnvironmentMixin.__init__(self)
        if self.log_level_channel:
            self.setup_level_channel(self.env)
        self.command = ChannelCommandProcessor(self.env, self.logger)
        self.config = config

        async def poll(args: Namespace, __: Optional[FieldOrChannel]) -> None:
            """Handle a test command."""

            count = 1
            delay = 0.0

            if args.extra:
                count = int(args.extra[0])
                if len(args.extra) > 1:
                    delay = float(args.extra[1])

            for _ in range(count):
                self.poll()
                await asyncio.sleep(delay)

        self._setup_async_commands(poll)

    def poll(self) -> None:
        """
        A method that other runtime entities can call to perform canonical
        updates to this struct's environment.
        """


StructMap = dict[str, RuntimeStructBase]
