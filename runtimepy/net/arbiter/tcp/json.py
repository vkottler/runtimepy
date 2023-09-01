"""
A module implementing JSON-message connection factories.
"""

# internal
from runtimepy.net.stream import UdpPrefixedMessageConnection
from runtimepy.net.stream.json import JsonMessageConnection
from runtimepy.net.tcp.connection import TcpConnection
from runtimepy.net.websocket import WebsocketConnection


class TcpJsonMessageConnection(JsonMessageConnection, TcpConnection):
    """A TCP connection interface for JSON messaging."""


class UdpJsonMessageConnection(
    JsonMessageConnection, UdpPrefixedMessageConnection
):
    """A UDP connection interface for JSON messaging."""


class WebsocketJsonMessageConnection(
    JsonMessageConnection, WebsocketConnection
):
    """A websocket connection interface for JSON messaging."""
