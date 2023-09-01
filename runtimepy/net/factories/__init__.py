"""
A module aggregating commonly used connection factory classes.
"""

# internal
from runtimepy.net.arbiter.tcp import TcpConnectionFactory
from runtimepy.net.arbiter.tcp.json import (
    TcpJsonMessageConnection,
    UdpJsonMessageConnection,
    WebsocketJsonMessageConnection,
)
from runtimepy.net.arbiter.udp import UdpConnectionFactory
from runtimepy.net.arbiter.websocket import WebsocketConnectionFactory
from runtimepy.net.stream import (
    EchoTcpMessageConnection,
    EchoUdpMessageConnection,
    TcpPrefixedMessageConnection,
    UdpPrefixedMessageConnection,
)
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
    "TcpMessage",
    "TcpMessageEcho",
    "TcpNull",
    "UdpConnection",
    "UdpConnectionFactory",
    "UdpEcho",
    "UdpMessage",
    "UdpMessageEcho",
    "UdpNull",
    "WebsocketConnection",
    "WebsocketConnectionFactory",
    "WebsocketEcho",
    "WebsocketNull",
]


class UdpEcho(UdpConnectionFactory[EchoUdpConnection]):
    """UDP echo-connection factory."""

    kind = EchoUdpConnection


class UdpMessage(UdpConnectionFactory[UdpPrefixedMessageConnection]):
    """UDP message-connection factory."""

    kind = UdpPrefixedMessageConnection


class UdpMessageEcho(UdpConnectionFactory[EchoUdpMessageConnection]):
    """UDP echo-connection factory."""

    kind = EchoUdpMessageConnection


class UdpNull(UdpConnectionFactory[NullUdpConnection]):
    """UDP null-connection factory."""

    kind = NullUdpConnection


class UdpJson(UdpConnectionFactory[UdpJsonMessageConnection]):
    """UDP JSON-connection factory."""

    kind = UdpJsonMessageConnection


class TcpEcho(TcpConnectionFactory[EchoTcpConnection]):
    """TCP echo-connection factory."""

    kind = EchoTcpConnection


class TcpMessage(TcpConnectionFactory[TcpPrefixedMessageConnection]):
    """TCP message-connection factory."""

    kind = TcpPrefixedMessageConnection


class TcpMessageEcho(TcpConnectionFactory[EchoTcpMessageConnection]):
    """TCP message-connection factory."""

    kind = EchoTcpMessageConnection


class TcpNull(TcpConnectionFactory[NullTcpConnection]):
    """TCP null-connection factory."""

    kind = NullTcpConnection


class TcpJson(TcpConnectionFactory[TcpJsonMessageConnection]):
    """TCP JSON-connection factory."""

    kind = TcpJsonMessageConnection


class WebsocketEcho(WebsocketConnectionFactory[EchoWebsocketConnection]):
    """WebSocket echo-connection factory."""

    kind = EchoWebsocketConnection


class WebsocketNull(WebsocketConnectionFactory[NullWebsocketConnection]):
    """WebSocket null-connection factory."""

    kind = NullWebsocketConnection


class WebsocketJson(
    WebsocketConnectionFactory[WebsocketJsonMessageConnection]
):
    """WebSocket JSON-connection factory."""

    kind = WebsocketJsonMessageConnection
