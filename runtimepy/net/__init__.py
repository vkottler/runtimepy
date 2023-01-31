"""
A module implementing various networking utilities.
"""

# built-in
import socket as _socket
from typing import Tuple as _Tuple


def get_free_socket(
    interface_ip: str = "",
    test_port: int = 0,
    family: int = _socket.AF_INET,
    kind: int = _socket.SOCK_STREAM,
    reuse: bool = False,
) -> _socket.SocketType:
    """Attempt to get an available socket."""

    sock = _socket.socket(family, kind)
    if reuse:
        sock.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
    sock.bind((interface_ip, test_port))
    return sock


def get_free_socket_name(
    interface_ip: str = "",
    test_port: int = 0,
    family: int = _socket.AF_INET,
    kind: int = _socket.SOCK_STREAM,
) -> _Tuple[str, int]:
    """
    Create a socket to determine an arbitrary port number that's available.
    There is an inherent race condition using this strategy.
    """

    sock = get_free_socket(
        interface_ip=interface_ip,
        test_port=test_port,
        family=family,
        reuse=True,
        kind=kind,
    )
    name, port = sock.getsockname()
    sock.close()

    assert isinstance(port, int)
    return name, port
