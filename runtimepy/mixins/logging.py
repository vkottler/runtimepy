"""
A module implementing a logger-mixin extension.
"""

# built-in
import logging

# third-party
from vcorelib.logging import LoggerMixin

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
