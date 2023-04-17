"""
A module implementing a connection arbiter interface.
"""

# built-in
from runtimepy.net.arbiter.base import NetworkApplication
from runtimepy.net.arbiter.config import (
    ConfigConnectionArbiter as _ConfigConnectionArbiter,
)
from runtimepy.net.arbiter.info import AppInfo, ConnectionMap

__all__ = [
    "AppInfo",
    "ConnectionArbiter",
    "ConnectionMap",
    "NetworkApplication",
]


class ConnectionArbiter(_ConfigConnectionArbiter):
    """A class implementing a connection manager for a broader application."""
