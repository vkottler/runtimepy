"""
A module implementing various networking utilities.
"""

# built-in
import socket as _socket
from typing import Tuple as _Tuple


def get_free_socket_name(
    interface_ip: str = "0.0.0.0",
    test_port: int = 0,
    family: int = _socket.AF_INET,
    kind: int = _socket.SOCK_STREAM,
) -> _Tuple[str, int]:
    """
    Create a socket to determine an arbitrary port number that's available.
    There is an inherent race condition using this strategy.
    """

    sock = _socket.socket(family, kind)
    sock.bind((interface_ip, test_port))
    sock.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
    name, port = sock.getsockname()
    sock.close()

    assert isinstance(port, int)
    return name, port
