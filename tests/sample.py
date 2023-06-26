"""
A module containing sample connection factories.
"""

# module under test
from runtimepy.net.arbiter import TaskFactory
from runtimepy.net.arbiter.tcp import TcpConnectionFactory
from runtimepy.net.arbiter.udp import UdpConnectionFactory
from runtimepy.net.arbiter.websocket import WebsocketConnectionFactory

# internal
from tests.resources import (
    SampleArbiterTask,
    SampleTcpConnection,
    SampleUdpConnection,
    SampleWebsocketConnection,
)


class SampleTaskFactoryA(TaskFactory[SampleArbiterTask]):
    """A sample task factory."""

    kind = SampleArbiterTask


class SampleTaskFactoryB(TaskFactory[SampleArbiterTask]):
    """A sample task factory."""

    kind = SampleArbiterTask


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
