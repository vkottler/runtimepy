"""
Test the 'net.arbiter' module.
"""

# built-in
from contextlib import AsyncExitStack as _AsyncExitStack

# third-party
from pytest import mark

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


def test_connection_arbiter_run():
    """Test the synchronous 'run' entry."""

    arbiter = ConnectionArbiter()
    assert arbiter.run() == 0


@mark.asyncio
async def test_connection_arbiter_basic():
    """Test basic interactions with a connection arbiter."""

    arbiter = ConnectionArbiter()

    # Register connection factories.
    assert arbiter.register_factory(SampleUdpConn(), "udp", "sample") is True
    assert arbiter.register_factory(SampleTcpConn(), "tcp", "sample") is True
    assert (
        arbiter.register_factory(SampleWebsocketConn(), "websocket", "sample")
        is True
    )

    # Register a few UDP connections.
    assert (
        await arbiter.factory_client(
            "SampleUdpConn", "a", local_addr=("localhost", 0)
        )
        is True
    )
    assert (
        await arbiter.factory_client(
            "sample_udp_conn", "b", local_addr=("localhost", 0)
        )
        is True
    )
    assert (
        await arbiter.factory_client(
            "sample_udp_conn", "c", local_addr=("localhost", 0)
        )
        is True
    )

    # Register a few TCP and WebSocket servers.
    for _ in range(3):
        assert await arbiter.factory_server("sample_tcp_conn", port=0) is True
        assert (
            await arbiter.factory_server(
                "sample_websocket_conn", host="0.0.0.0", port=0
            )
            is True
        )

    async with _AsyncExitStack() as stack:
        # Start a TCP server.
        tcp_server = await stack.enter_async_context(
            SampleTcpConnection.serve(port=0, backlog=3)
        )
        tcp_port = tcp_server.sockets[0].getsockname()[1]

        # Register a few TCP connections.
        for name in "abc":
            assert (
                await arbiter.factory_client(
                    "sample_tcp_conn", name, host="localhost", port=tcp_port
                )
                is True
            )

        # Start a WebSocket server.
        websocket_server = await stack.enter_async_context(
            SampleWebsocketConnection.serve(
                stop_sig=arbiter.stop_sig,
                host="0.0.0.0",
                port=0,
            )
        )
        websocket_port = list(websocket_server.sockets)[0].getsockname()[1]

        # Register a few WebSocket connections.
        for name in "abc":
            assert (
                await arbiter.factory_client(
                    "sample_websocket_conn",
                    name,
                    f"ws://localhost:{websocket_port}",
                )
                is True
            )

        # Run the application.
        assert await arbiter.app() == 0
