"""
A module implementing package utilities.
"""

# built-in
import logging
import re
from typing import Iterable, Iterator

# third-party
from vcorelib.logging import DEFAULT_TIME_FORMAT
from vcorelib.paths.context import PossiblePath, as_path

# Continue exporting some migrated things.
__all__ = [
    "ListLogger",
    "as_path",
    "import_str_and_item",
    "name_search",
    "Identifier",
    "PossiblePath",
]


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


def import_str_and_item(module_path: str) -> tuple[str, str]:
    """
    Treat the last entry in a '.' delimited string as the item to import from
    the module in the string preceding it.
    """

    parts = module_path.split(".")
    assert len(parts) > 1, module_path

    item = parts.pop()
    return ".".join(parts), item


def name_search(
    names: Iterable[str], pattern: str, exact: bool = False
) -> Iterator[str]:
    """A simple name searching method."""

    compiled = re.compile(pattern)
    for name in names:
        if compiled.search(name) is not None:
            if not exact or name == pattern:
                yield name


class Identifier:
    """A simple message indentifier interface."""

    def __init__(self) -> None:
        """Initialize this instance."""
        self.curr_id: int = 1
        self.scale = 2

    def __call__(self) -> int:
        """Get the next identifier."""
        curr = self.curr_id
        self.curr_id += self.scale
        return curr
