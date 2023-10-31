"""
A module implementing various networking utilities.
"""

# built-in
from contextlib import suppress as _suppress
import socket as _socket
from typing import Awaitable, NamedTuple, Optional, TypeVar
from typing import Union as _Union

# third-party
from vcorelib.logging import LoggerType


class IPv4Host(NamedTuple):
    """See: https://docs.python.org/3/library/socket.html#socket-families."""

    name: str = ""
    port: int = 0

    def __str__(self) -> str:
        """Get this host as a string."""
        return hostname_port(self.name, self.port)


class IPv6Host(NamedTuple):
    """See: https://docs.python.org/3/library/socket.html#socket-families."""

    name: str = ""
    port: int = 0
    flowinfo: int = 0
    scope_id: int = 0

    def __str__(self) -> str:
        """Get this host as a string."""
        return hostname_port(self.name, self.port)


IpHost = _Union[IPv4Host, IPv6Host]
IpHostlike = _Union[str, int, IpHost, None]


def normalize_host(*args: IpHostlike) -> IpHost:
    """Get a host object from caller parameters."""

    # Default.
    if args[0] is None:
        return IPv4Host()

    if isinstance(args[0], (IPv4Host, IPv6Host)):
        return args[0]

    if len([*args]) == 2:
        return IPv4Host(*args)  # type: ignore
    return IPv6Host(*args)  # type: ignore


def hostname(ip_address: str) -> str:
    """
    Attempt to get a string hostname for a string IP address argument that
    'gethostbyaddr' accepts. Otherwise return the original string
    """
    result = ip_address
    with _suppress(_socket.herror, OSError):
        result = _socket.gethostbyaddr(ip_address)[0]
    return result


def hostname_port(ip_address: str, port: int) -> str:
    """Get a hostname string with a port appended."""
    return f"{hostname(ip_address)}:{port}"


def sockname(sock: _socket.SocketType) -> IpHost:
    """Get address information from a socket."""

    assert sock.family == _socket.AF_INET
    return normalize_host(*sock.getsockname())


def get_free_socket(
    local: IpHost = None,
    kind: int = _socket.SOCK_STREAM,
    reuse: bool = False,
) -> _socket.SocketType:
    """Attempt to get an available socket."""

    local = normalize_host(local)

    sock = _socket.socket(_socket.AF_INET, kind)
    if reuse:
        sock.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
    sock.bind((local.name, local.port))
    return sock


def get_free_socket_name(
    local: IpHost = None, kind: int = _socket.SOCK_STREAM
) -> IpHost:
    """
    Create a socket to determine an arbitrary port number that's available.
    There is an inherent race condition using this strategy.
    """

    sock = get_free_socket(local=local, reuse=True, kind=kind)
    name = sockname(sock)
    sock.close()
    return name


T = TypeVar("T")


async def try_log_connection_error(
    future: Awaitable[T], message: str, logger: LoggerType = None
) -> Optional[T]:
    """
    Attempt to resolve a future but log any connection-related exceptions.
    """

    result = None

    try:
        result = await future
    except ConnectionError as exc:
        if logger:
            logger.exception(message, exc_info=exc)

    return result
