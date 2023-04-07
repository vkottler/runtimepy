"""
A module implementing a connection arbiter interface.
"""

# built-in
from runtimepy.net.arbiter.base import ConnectionMap, NetworkApplication
from runtimepy.net.arbiter.factory import (
    FactoryConnectionArbiter as _FactoryConnectionArbiter,
)

__all__ = ["ConnectionMap", "NetworkApplication"]


class ConnectionArbiter(_FactoryConnectionArbiter):
    """A class implementing a connection manager for a broader application."""
