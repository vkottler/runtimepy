"""
Test the 'net.arbiter.config' module.
"""

# built-in
from typing import cast

# third-party
from pytest import mark

# module under test
from runtimepy.net.arbiter import AppInfo, ConnectionArbiter

# internal
from tests.resources import (
    SampleConnectionMixin,
    SampleUdpConnection,
    resource,
)


@mark.asyncio
async def test_connection_arbiter_config_basic():
    """Test basic loading of the connection-arbiter config."""

    arbiter = ConnectionArbiter()

    # Register clients and servers from the config.
    await arbiter.load_config(resource("connection_arbiter", "basic.yaml"))

    assert await arbiter.app() == 0


async def echo_test_app(app: AppInfo) -> int:
    """Test some of the echo connections."""

    # Ensure that configuration data got set correctly.
    assert app.config == {"a": 1, "b": 2, "c": 3}

    assert len(list(app.search(pattern="sample"))) == 3
    assert len(list(app.search(kind=SampleUdpConnection))) == 1

    conns = [
        "tcp.sample.client",
        "udp.sample.client",
        "websocket.sample.client",
    ]
    for name in conns:
        assert name in app.connections
        conn: SampleConnectionMixin = cast(
            SampleConnectionMixin, app.connections[name]
        )

        # Send a message.
        conn.send_text("Hello, world!\nabc\n123")
        await conn.message_rx.acquire()

    return 0


@mark.asyncio
async def test_connection_arbiter_config_echo():
    """Test various 'echo' connection types."""

    arbiter = ConnectionArbiter(app=echo_test_app)

    # Register clients and servers from the config.
    await arbiter.load_config(resource("connection_arbiter", "test_echo.yaml"))

    assert await arbiter.app() == 0
