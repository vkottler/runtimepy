"""
A module containing sample connection factories.
"""

# module under test
from runtimepy.net.arbiter import TaskFactory
from runtimepy.net.arbiter.config import ConfigObject
from runtimepy.net.arbiter.tcp import TcpConnectionFactory
from runtimepy.net.arbiter.udp import UdpConnectionFactory
from runtimepy.net.arbiter.websocket import WebsocketConnectionFactory
from runtimepy.net.stream import (
    TcpStringMessageConnection,
    UdpStringMessageConnection,
)

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


class TcpString(TcpConnectionFactory[TcpStringMessageConnection]):
    """A string-message connection factory for TCP."""

    kind = TcpStringMessageConnection


class UdpString(UdpConnectionFactory[UdpStringMessageConnection]):
    """A string-message connection factory for UDP."""

    kind = UdpStringMessageConnection


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


def config(data: ConfigObject) -> None:
    """Sample config-builder method."""

    del data
