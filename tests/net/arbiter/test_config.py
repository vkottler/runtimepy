"""
Test the 'net.arbiter.config' module.
"""

# built-in
import asyncio
from typing import cast

# third-party
from pytest import mark

# module under test
from runtimepy.net.arbiter import AppInfo, ConnectionArbiter
from runtimepy.net.stream import PrefixedMessageConnection

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
    await arbiter.load_configs([resource("connection_arbiter", "basic.yaml")])

    assert await arbiter.app() == 0


@mark.asyncio
async def test_connection_arbiter_config_fails():
    """Test failure handing."""

    for config in ["basic_fail.yaml", "basic_exception.yaml"]:
        arbiter = ConnectionArbiter()
        await arbiter.load_configs([resource("connection_arbiter", config)])
        assert await arbiter.app() != 0


async def echo_message_test_app(app: AppInfo) -> int:
    """Test message connections."""

    senders = list(app.search(pattern="null", kind=PrefixedMessageConnection))
    assert len(senders) == 2

    for _ in range(2):
        for idx in range(4096):
            msg = f"Hello, world! ({idx})"
            for sender in senders:
                sender.send_message_str(msg)
        await asyncio.sleep(0)

    return 0


async def echo_test_app(app: AppInfo) -> int:
    """Test some of the echo connections."""

    # Ensure that configuration data got set correctly.
    if "root" in app.config:
        del app.config["root"]
    assert app.config == {"a": 1, "b": 2, "c": 3}

    assert len(list(app.search(pattern="sample"))) == 3
    assert len(list(app.search(kind=SampleUdpConnection))) == 1
    assert app.single(kind=SampleUdpConnection)

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

    arbiter = ConnectionArbiter(app=[echo_test_app, echo_message_test_app])

    # Register clients and servers from the config.
    await arbiter.load_configs(
        [resource("connection_arbiter", "test_echo.yaml")]
    )

    assert await arbiter.app() == 0
