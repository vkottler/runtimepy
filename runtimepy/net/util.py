"""
A module implementing various networking utilities.
"""

# built-in
from contextlib import suppress as _suppress
from functools import cache
import ipaddress
import socket as _socket
from typing import Awaitable, NamedTuple, Optional, TypeVar
from typing import Union as _Union

# third-party
from vcorelib.logging import LoggerType


class IPv4Host(NamedTuple):
    """See: https://docs.python.org/3/library/socket.html#socket-families."""

    name: str = ""
    port: int = 0

    @property
    def family(self) -> int:
        """Address family constant."""
        return _socket.AF_INET

    def zero_port(self) -> "IPv4Host":
        """Get a zeroed-out port instance."""

        return self if self.port == 0 else IPv4Host(self.name, 0)

    @property
    def hostname(self) -> str:
        """Get a hostname for this instance."""
        return hostname(self.name)

    @property
    def address(self) -> ipaddress.IPv4Address:
        """Get an address object for this hostname."""
        return ipaddress.IPv4Address(self.address_str)

    @property
    def address_str(self) -> str:
        """Get an address string for this host."""
        return address_str(
            self.name, family=self.family, fallback_host="0.0.0.0"
        )

    @property
    def address_str_tuple(self) -> tuple[str, int]:
        """Get a string-address tuple for this instance."""
        return (self.address_str, self.port)

    def __str__(self) -> str:
        """Get this host as a string."""
        return hostname_port(self.name, self.port)

    def __hash__(self) -> int:
        """Get a hash for this instance."""
        return hash(str(self))


class IPv6Host(NamedTuple):
    """See: https://docs.python.org/3/library/socket.html#socket-families."""

    name: str = ""
    port: int = 0
    flowinfo: int = 0
    scope_id: int = 0

    @property
    def hostname(self) -> str:
        """Get a hostname for this instance."""
        return hostname(self.name)

    @property
    def address(self) -> ipaddress.IPv6Address:
        """Get an address object for this hostname."""
        return ipaddress.IPv6Address(self.address_str)

    def zero_port(self) -> "IPv6Host":
        """Get a zeroed-out port instance."""

        return (
            self
            if self.port == 0
            else IPv6Host(self.name, 0, self.flowinfo, self.scope_id)
        )

    @property
    def family(self) -> int:
        """Address family constant."""
        return _socket.AF_INET6

    @property
    def address_str(self) -> str:
        """Get an address string for this host."""
        return address_str(self.name, family=self.family, fallback_host="::")

    @property
    def address_str_tuple(self) -> tuple[str, int, int, int]:
        """Get a string-address tuple for this instance."""
        return (self.address_str, self.port, self.flowinfo, self.scope_id)

    def __str__(self) -> str:
        """Get this host as a string."""
        return hostname_port(self.name, self.port)

    def __hash__(self) -> int:
        """Get a hash for this instance."""
        return hash(str(self))


IpHost = _Union[IPv4Host, IPv6Host]
IpHostlike = _Union[str, int, IpHost, None]
IpHostTuplelike = _Union[IpHost, tuple[str, int], tuple[str, int, int, int]]


def normalize_host(
    *args: IpHostlike, default: type[IpHost] = IPv4Host
) -> IpHost:
    """Get a host object from caller parameters."""

    # Default.
    if not args or args[0] is None:
        return default()

    if isinstance(args[0], (IPv4Host, IPv6Host)):
        return args[0]

    if len([*args]) <= 2:
        return IPv4Host(*args)  # type: ignore
    return IPv6Host(*args)  # type: ignore


USE_FQDN = {"::", "0.0.0.0"}


@cache
def hostname(ip_address: str) -> str:
    """
    Attempt to get a string hostname for a string IP address argument that
    'gethostbyaddr' accepts. Otherwise return the original string
    """

    result = ip_address

    if ip_address in USE_FQDN:
        result = _socket.getfqdn()
    else:
        with _suppress(_socket.herror, OSError):
            result = _socket.gethostbyaddr(ip_address)[0]

    return result


@cache
def address_str(name: str, fallback_host: str = "localhost", **kwargs) -> str:
    """Get an IP address string for a given name."""

    return _socket.getaddrinfo(  # type: ignore
        name if name else fallback_host, None, **kwargs
    )[0][4][0]


@cache
def hostname_port(ip_address: str, port: int) -> str:
    """Get a hostname string with a port appended."""
    return f"{hostname(ip_address)}:{port}"


def sockname(sock: _socket.SocketType) -> IpHost:
    """Get address information from a socket."""
    return normalize_host(*sock.getsockname())


def get_free_socket(
    local: IpHost = None,
    kind: int = _socket.SOCK_STREAM,
    reuse: bool = False,
) -> _socket.SocketType:
    """Attempt to get an available socket."""

    local = normalize_host(local)

    sock = _socket.socket(local.family, kind)
    if reuse:
        sock.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
    sock.bind(local.address_str_tuple)
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
