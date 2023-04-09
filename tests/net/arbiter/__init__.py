"""
Utilities for testing the connection arbiter.
"""

# module under test
from runtimepy.net.arbiter import ConnectionArbiter
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


def get_test_arbiter() -> ConnectionArbiter:
    """
    Get a connection arbiter with some basic connection factories registered.
    """

    arbiter = ConnectionArbiter()

    # Register connection factories.
    assert arbiter.register_factory(SampleUdpConn(), "udp", "sample")
    assert arbiter.register_factory(SampleTcpConn(), "tcp", "sample")
    assert arbiter.register_factory(
        SampleWebsocketConn(), "websocket", "sample"
    )

    return arbiter
