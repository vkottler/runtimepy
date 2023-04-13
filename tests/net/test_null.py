"""
Test Null variants of connection interfaces.
"""

# built-in
import asyncio

# third-party
from pytest import mark

# module under test
from runtimepy.net.arbiter import ConnectionArbiter
from runtimepy.net.arbiter.base import AppInfo

# internal
from tests.resources import resource


async def spam_app(app: AppInfo) -> int:
    """Waits for the stop signal to be set."""

    iterations: int = app.config.get("iterations", 3)  # type: ignore

    for _ in range(iterations):
        for name, conn in app.connections.items():
            # Send random data.
            if "null" in name:
                msg = "Hello, world!\n"
                conn.send_text(msg)
                conn.send_binary(msg.encode())

        # Allow the connections to be servied.
        await asyncio.sleep(0.01)

    return 0


@mark.asyncio
async def test_null_connections_app():
    """Test various null connection types."""

    arbiter = ConnectionArbiter()
    await arbiter.load_config(resource("connection_arbiter", "test_null.yaml"))
    assert await arbiter.app() == 0
