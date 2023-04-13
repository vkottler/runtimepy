"""
A module aggregating all TCP-related interfaces.
"""

# internal
from runtimepy.net.tcp.connection import (
    EchoTcpConnection,
    NullTcpConnection,
    TcpConnection,
)

__all__ = ["TcpConnection", "EchoTcpConnection", "NullTcpConnection"]
