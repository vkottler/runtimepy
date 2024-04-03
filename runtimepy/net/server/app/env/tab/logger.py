"""
A module implementing a simple logger interface for tabs.
"""

# built-in
import logging
from typing import Callable

# third-party
from vcorelib.logging import DEFAULT_TIME_FORMAT

# internal
from runtimepy.net.stream.json.types import JsonMessage

TabMessageSender = Callable[[JsonMessage], None]


class TabLogger(logging.Handler):
    """An interface facilitating sending log messages to browser tabs."""

    send: TabMessageSender

    def emit(self, record):
        """Send the log message."""
        self.send({"log_message": self.format(record)})

    @staticmethod
    def create(send: TabMessageSender) -> "TabLogger":
        """Create a tab logger handler."""

        handler = TabLogger()
        handler.send = send
        handler.setFormatter(logging.Formatter(DEFAULT_TIME_FORMAT))
        return handler
