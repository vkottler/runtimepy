"""
A module aggregating commonly used connection factory classes.
"""

# internal
from runtimepy.net.arbiter.tcp import TcpConnectionFactory
from runtimepy.net.arbiter.udp import UdpConnectionFactory
from runtimepy.net.arbiter.websocket import WebsocketConnectionFactory
from runtimepy.net.tcp import (
    EchoTcpConnection,
    NullTcpConnection,
    TcpConnection,
)
from runtimepy.net.udp import (
    EchoUdpConnection,
    NullUdpConnection,
    UdpConnection,
)
from runtimepy.net.websocket import (
    EchoWebsocketConnection,
    NullWebsocketConnection,
    WebsocketConnection,
)

# Expose a number of useful symbols in one place.
__all__ = [
    "TcpConnection",
    "TcpConnectionFactory",
    "TcpEcho",
    "TcpNull",
    "UdpConnection",
    "UdpConnectionFactory",
    "UdpEcho",
    "UdpNull",
    "WebsocketConnection",
    "WebsocketConnectionFactory",
    "WebsocketEcho",
    "WebsocketNull",
]


class UdpEcho(UdpConnectionFactory[EchoUdpConnection]):
    """UDP echo-connection factory."""

    kind = EchoUdpConnection


class UdpNull(UdpConnectionFactory[NullUdpConnection]):
    """UDP null-connection factory."""

    kind = NullUdpConnection


class TcpEcho(TcpConnectionFactory[EchoTcpConnection]):
    """TCP echo-connection factory."""

    kind = EchoTcpConnection


class TcpNull(TcpConnectionFactory[NullTcpConnection]):
    """TCP null-connection factory."""

    kind = NullTcpConnection


class WebsocketEcho(WebsocketConnectionFactory[EchoWebsocketConnection]):
    """WebSocket echo-connection factory."""

    kind = EchoWebsocketConnection


class WebsocketNull(WebsocketConnectionFactory[NullWebsocketConnection]):
    """WebSocket null-connection factory."""

    kind = NullWebsocketConnection
