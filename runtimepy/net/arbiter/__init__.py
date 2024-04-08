"""
A module implementing a connection arbiter interface.
"""

# built-in
from runtimepy.net.arbiter.base import init_only
from runtimepy.net.arbiter.config import (
    ConfigConnectionArbiter as _ConfigConnectionArbiter,
)
from runtimepy.net.arbiter.info import (
    AppInfo,
    ConnectionMap,
    NetworkApplication,
)
from runtimepy.net.arbiter.task import (
    ArbiterTask,
    ArbiterTaskManager,
    TaskFactory,
)

__all__ = [
    "AppInfo",
    "ArbiterTask",
    "ArbiterTaskManager",
    "ConnectionArbiter",
    "ConnectionMap",
    "NetworkApplication",
    "init_only",
    "TaskFactory",
]


class ConnectionArbiter(_ConfigConnectionArbiter):
    """A class implementing a connection manager for a broader application."""
