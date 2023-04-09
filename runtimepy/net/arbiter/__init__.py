"""
A module implementing a connection arbiter interface.
"""

# built-in
from runtimepy.net.arbiter.base import ConnectionMap, NetworkApplication
from runtimepy.net.arbiter.config import (
    ConfigConnectionArbiter as _ConfigConnectionArbiter,
)

__all__ = ["ConnectionMap", "NetworkApplication"]


class ConnectionArbiter(_ConfigConnectionArbiter):
    """A class implementing a connection manager for a broader application."""
