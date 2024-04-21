"""
A module implementing package utilities.
"""

# built-in
import logging
from typing import NamedTuple

# third-party
from vcorelib.logging import DEFAULT_TIME_FORMAT


class StrToBool(NamedTuple):
    """A container for results when converting strings to boolean."""

    result: bool
    valid: bool

    @staticmethod
    def parse(data: str) -> "StrToBool":
        """Parse a string to boolean."""

        data = data.lower()
        is_true = data == "true"
        resolved = is_true or data == "false"
        return StrToBool(is_true, resolved)


class ListLogger(logging.Handler):
    """An interface facilitating sending log messages to browser tabs."""

    log_messages: list[logging.LogRecord]

    def drain(self) -> list[logging.LogRecord]:
        """Drain messages."""

        result = self.log_messages
        self.log_messages = []
        return result

    def drain_str(self) -> list[str]:
        """Drain formatted messages."""

        return [self.format(x) for x in self.drain()]

    def __bool__(self) -> bool:
        """Evaluate this instance as boolean."""
        return bool(self.log_messages)

    def emit(self, record: logging.LogRecord) -> None:
        """Send the log message."""

        self.log_messages.append(record)

    @staticmethod
    def create() -> "ListLogger":
        """Create an instance of this handler."""

        logger = ListLogger()
        logger.log_messages = []
        logger.setFormatter(logging.Formatter(DEFAULT_TIME_FORMAT))

        return logger
