"""
A module implementing a logger-mixin extension.
"""

# built-in
from contextlib import AsyncExitStack
import io
import logging
from typing import Any, Iterable

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


LogLevellike = LogLevel | int | str


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


LogPaths = Iterable[tuple[LogLevellike, Pathlike]]


class LogCaptureMixin:
    """A simple async file-reading interface."""

    logger: LoggerType

    # Open aiofiles handles.
    streams: list[tuple[int, Any]]

    ext_log_extra = {"external": True}

    async def init_log_capture(
        self, stack: AsyncExitStack, log_paths: LogPaths
    ) -> None:
        """Initialize this task with application information."""

        self.streams = [
            (
                LogLevel.normalize(level),
                await stack.enter_async_context(aiofiles.open(path, mode="r")),
            )
            for level, path in log_paths
            if normalize(path).is_file()
        ]

        # Don't handle any kind of backhaul.
        for stream in self.streams:
            await stream[1].seek(0, io.SEEK_END)

    def log_line(self, level: int, data: str) -> None:
        """Log a line for output."""
        self.logger.log(level, data, extra=self.ext_log_extra)

    async def dispatch_log_capture(self) -> None:
        """Get the next line from this log stream."""

        for level, stream in self.streams:
            line = (await stream.readline()).rstrip()
            while line:
                self.log_line(level, line)
                line = (await stream.readline()).rstrip()
