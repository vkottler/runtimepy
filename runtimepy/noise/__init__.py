"""
A module implementing a structure that simulates a configurable noise source.
"""

# built-in
import random

# internal
from runtimepy.control.source import DoubleSource


class GaussianSource(DoubleSource):
    """A simple output-source struct."""

    def source(self, index: int) -> float:
        """Provide the next value."""

        del index
        return random.gauss()
