"""
A module implementing a simple logger interface for tabs.
"""

# built-in
import logging
from typing import Callable

# internal
from runtimepy.net.stream.json.types import JsonMessage

TabMessageSender = Callable[[JsonMessage], None]


class ListLogger(logging.Handler):
    """An interface facilitating sending log messages to browser tabs."""

    log_messages: list[str]

    def emit(self, record):
        """Send the log message."""

        self.log_messages.append(self.format(record))
