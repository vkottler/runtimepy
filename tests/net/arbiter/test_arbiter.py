"""
Test the 'net.arbiter' module.
"""

# built-in
from contextlib import AsyncExitStack as _AsyncExitStack

# third-party
from pytest import mark

# module under test
from runtimepy.net import get_free_socket_name
from runtimepy.net.apps import init_only
from runtimepy.net.arbiter import AppInfo, ConnectionArbiter

# internal
from tests.net.arbiter import get_test_arbiter
from tests.resources import (
    SampleArbiterTask,
    SampleTcpConnection,
    SampleWebsocketConnection,
)


async def assertion_failer(app: AppInfo) -> int:
    """An app task that raises an assertion."""

    assert app
    assert False, "nominal failure"
    return 0


def test_connection_arbiter_run():
    """Test the synchronous 'run' entry."""

    arbiter = ConnectionArbiter()
    assert arbiter.task_manager.register(
        SampleArbiterTask("sample"), period_s=0.05
    )
    assert arbiter.run(app=init_only) == 0
    assert arbiter.run(app=assertion_failer) != 0


@mark.asyncio
async def test_connection_arbiter_basic():
    """Test basic interactions with a connection arbiter."""

    arbiter = get_test_arbiter()

    # Register a few UDP connections.
    for name in "abc":
        assert await arbiter.factory_client(
            "SampleUdpConn", name, local_addr=("localhost", 0)
        )

    # Register a few TCP and WebSocket servers.
    for _ in range(3):
        assert await arbiter.factory_server("sample_tcp_conn", port=0)
        assert await arbiter.factory_server(
            "sample_websocket_conn", host="0.0.0.0", port=0
        )

    # Register a few deferred TCP clients.
    tcp_port = get_free_socket_name().port
    assert await arbiter.factory_server("sample_tcp_conn", port=tcp_port)
    for name in "def":
        assert await arbiter.factory_client(
            "sample_tcp_conn",
            name,
            host="localhost",
            defer=True,
            port=tcp_port,
        )

    async with _AsyncExitStack() as stack:
        # Start a TCP server.
        tcp_server = await stack.enter_async_context(
            SampleTcpConnection.serve(port=0, backlog=3)
        )
        tcp_port = tcp_server.sockets[0].getsockname()[1]

        # Register a few TCP connections.
        for name in "abc":
            assert await arbiter.factory_client(
                "sample_tcp_conn", name, host="localhost", port=tcp_port
            )

        # Start a WebSocket server.
        websocket_server = await stack.enter_async_context(
            SampleWebsocketConnection.serve(
                stop_sig=arbiter.stop_sig,
                manager=arbiter.manager,
                host="0.0.0.0",
                port=0,
            )
        )
        websocket_port = list(websocket_server.sockets)[0].getsockname()[1]

        # Register a few WebSocket connections.
        for name in "abc":
            assert await arbiter.factory_client(
                "sample_websocket_conn",
                name,
                f"ws://localhost:{websocket_port}",
            )

        # Run the application.
        assert await arbiter.app() == 0
