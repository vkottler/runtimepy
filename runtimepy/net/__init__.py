"""
A module aggregating commonly used networking interface.
"""

# internal
from runtimepy.net.backoff import ExponentialBackoff
from runtimepy.net.connection import (
    BinaryMessage,
    Connection,
    EchoConnection,
    NullConnection,
)
from runtimepy.net.manager import ConnectionManager
from runtimepy.net.util import (
    IpHost,
    IPv4Host,
    IPv6Host,
    get_free_socket,
    get_free_socket_name,
    hostname,
    normalize_host,
    sockname,
    try_log_connection_error,
)

__all__ = [
    "BinaryMessage",
    "Connection",
    "EchoConnection",
    "NullConnection",
    "ConnectionManager",
    "IpHost",
    "IPv4Host",
    "IPv6Host",
    "get_free_socket",
    "get_free_socket_name",
    "hostname",
    "normalize_host",
    "sockname",
    "ExponentialBackoff",
    "try_log_connection_error",
]
