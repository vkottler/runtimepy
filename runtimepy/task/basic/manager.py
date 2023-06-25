"""
A module implementing a periodic-task manager.
"""

# third-party
from vcorelib.logging import LoggerMixin as _LoggerMixin
from vcorelib.logging import LoggerType as _LoggerType


class PeriodicTaskManager(_LoggerMixin):
    """A class for managing periodic tasks as a single group."""

    def __init__(self, logger: _LoggerType = None) -> None:
        """Initialize this instance."""

        super().__init__(logger=logger)
        print("todo")
