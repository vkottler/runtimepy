"""
A module implementing a stateful data interface for per-connection tabs.
"""

# built-in
from collections import defaultdict
from dataclasses import dataclass
import logging

# third-party
from vcorelib.logging import ListLogger

# internal
from runtimepy.channel.environment.base import ValueMap
from runtimepy.message import JsonMessage
from runtimepy.primitives import AnyPrimitive

# (value, nanosecond timestamp)
Point = tuple[str | int | float | bool, int]


@dataclass
class TabState:
    """Stateful information relevant to individual tabs."""

    shown: bool
    tab_logger: ListLogger

    points: dict[str, list[Point]]
    primitives: dict[str, AnyPrimitive]
    callbacks: dict[str, int]

    latest_ui_values: ValueMap

    _loggers: list[logging.Logger]

    def frame(self, time: float) -> JsonMessage:
        """Handle a new UI frame."""

        # Not used yet.
        del time

        result: JsonMessage = {}

        # Handle log messages.
        if self.tab_logger:
            result["log_messages"] = self.tab_logger.drain_str()

        # Handle channel updates.
        if self.points:
            result["points"] = self.points
            self.points = defaultdict(list)

        return result

    def clear_loggers(self) -> None:
        """Clear all logging handlers."""

        for logger in self._loggers:
            logger.removeHandler(self.tab_logger)
        self._loggers = []

    def add_logger(self, logger: logging.Logger) -> None:
        """Add a logger."""

        logger.addHandler(self.tab_logger)
        self._loggers.append(logger)

    @staticmethod
    def create() -> "TabState":
        """Create a new instance."""

        return TabState(
            False, ListLogger.create(), defaultdict(list), {}, {}, {}, []
        )
