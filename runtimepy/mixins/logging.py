"""
A module implementing a logger-mixin extension.
"""

# built-in
from contextlib import AsyncExitStack
import io
import logging
import os
from pathlib import Path
from typing import Any

# third-party
import aiofiles
from vcorelib.logging import LoggerMixin, LoggerType
from vcorelib.paths import Pathlike, normalize

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.enum.registry import RuntimeIntEnum


class LogLevel(RuntimeIntEnum):
    """A runtime enumeration for log level."""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LoggerMixinLevelControl(LoggerMixin):
    """A logger mixin that exposes a runtime-controllable level."""

    def _log_level_changed(self, _: int, new_value: int) -> None:
        """Handle a change in log level."""

        self.logger.setLevel(new_value)
        self.logger.log(new_value, "Log level updated to %d.", new_value)

    def setup_level_channel(
        self,
        env: ChannelEnvironment,
        name: str = "log_level",
        initial: str = "info",
        description: str = "Text-log level filter for this environment.",
    ) -> None:
        """Add a commandable log-level channel to the environment."""

        chan = env.int_channel(
            name,
            enum=LogLevel.register_enum(env.enums),
            commandable=True,
            description=description,
        )

        # Set up change handler.
        chan[0].raw.register_callback(self._log_level_changed)

        # Set the initial log level.
        env.set(name, initial)

        del chan


SYSLOG = Path(os.sep, "var", "log", "syslog")


class LogCaptureMixin:
    """A simple async file-reading interface."""

    logger: LoggerType

    # Open aiofiles handles.
    streams: list[Any]

    async def init_log_capture(
        self, stack: AsyncExitStack, log_paths: list[Pathlike]
    ) -> None:
        """Initialize this task with application information."""

        self.streams = [
            await stack.enter_async_context(aiofiles.open(x, mode="r"))
            for x in log_paths
            if normalize(x).is_file()
        ]

        # Don't handle any kind of backhaul.
        for stream in self.streams:
            await stream.seek(0, io.SEEK_END)

    def log_line(self, data: str) -> None:
        """Log a line for output."""
        self.logger.info(data, extra={"external": True})

    async def next_lines(self) -> list[str]:
        """Get the next line from this log stream."""

        result = []
        for stream in self.streams:
            line = (await stream.readline()).rstrip()
            if line:
                result.append(line)
        return result

    async def dispatch_log_capture(self) -> None:
        """Check for new log data."""

        data = await self.next_lines()
        while data:
            for item in data:
                self.log_line(item)
            data = await self.next_lines()
