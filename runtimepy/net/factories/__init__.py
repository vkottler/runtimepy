"""
A module aggregating commonly used connection factory classes.
"""

# internal
from runtimepy.net.arbiter.tcp import TcpConnectionFactory
from runtimepy.net.arbiter.udp import UdpConnectionFactory
from runtimepy.net.arbiter.websocket import WebsocketConnectionFactory
from runtimepy.net.tcp.connection import EchoTcpConnection, TcpConnection
from runtimepy.net.udp.connection import EchoUdpConnection, UdpConnection
from runtimepy.net.websocket.connection import (
    EchoWebsocketConnection,
    WebsocketConnection,
)

# Expose a number of useful symbols in one place.
__all__ = [
    "TcpConnection",
    "TcpConnectionFactory",
    "TcpEcho",
    "UdpConnection",
    "UdpConnectionFactory",
    "UdpEcho",
    "WebsocketConnection",
    "WebsocketConnectionFactory",
    "WebsocketEcho",
]


class UdpEcho(UdpConnectionFactory[EchoUdpConnection]):
    """UDP echo-connection factory."""

    kind = EchoUdpConnection


class TcpEcho(TcpConnectionFactory[EchoTcpConnection]):
    """TCP echo-connection factory."""

    kind = EchoTcpConnection


class WebsocketEcho(WebsocketConnectionFactory[EchoWebsocketConnection]):
    """WebSocket echo-connection factory."""

    kind = EchoWebsocketConnection
