"""
A module implementing connection interfaces for stdio.
"""

# internal
from runtimepy.net.stream.connection import (
    EchoStreamConnection,
    NullStreamConnection,
    StreamConnection,
)

__all__ = ["EchoStreamConnection", "NullStreamConnection", "StreamConnection"]
