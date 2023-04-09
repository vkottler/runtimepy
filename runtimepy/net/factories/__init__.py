"""
A module aggregating commonly used connection factory classes.
"""

# internal
from runtimepy.net.arbiter.tcp import TcpConnectionFactory
from runtimepy.net.arbiter.udp import UdpConnectionFactory
from runtimepy.net.arbiter.websocket import WebsocketConnectionFactory
from runtimepy.net.tcp.connection import EchoTcpConnection
from runtimepy.net.udp.connection import EchoUdpConnection
from runtimepy.net.websocket.connection import EchoWebsocketConnection

__all__ = ["UdpEcho", "TcpEcho", "WebsocketEcho"]


class UdpEcho(UdpConnectionFactory[EchoUdpConnection]):
    """UDP echo-connection factory."""

    kind = EchoUdpConnection


class TcpEcho(TcpConnectionFactory[EchoTcpConnection]):
    """TCP echo-connection factory."""

    kind = EchoTcpConnection


class WebsocketEcho(WebsocketConnectionFactory[EchoWebsocketConnection]):
    """WebSocket echo-connection factory."""

    kind = EchoWebsocketConnection
