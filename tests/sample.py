"""
A module containing sample connection factories.
"""

# module under test
from runtimepy.net.arbiter.tcp import TcpConnectionFactory
from runtimepy.net.arbiter.udp import UdpConnectionFactory
from runtimepy.net.arbiter.websocket import WebsocketConnectionFactory

# internal
from tests.resources import (
    SampleTcpConnection,
    SampleUdpConnection,
    SampleWebsocketConnection,
)


class SampleUdpConn(UdpConnectionFactory[SampleUdpConnection]):
    """A connection factory for the sample UDP connection."""

    kind = SampleUdpConnection


class SampleTcpConn(TcpConnectionFactory[SampleTcpConnection]):
    """A connection factory for the sample TCP connection."""

    kind = SampleTcpConnection


class SampleWebsocketConn(
    WebsocketConnectionFactory[SampleWebsocketConnection]
):
    """A connection factory for the sample WebSocket connection."""

    kind = SampleWebsocketConnection