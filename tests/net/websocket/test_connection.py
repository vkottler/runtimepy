"""
Test the 'net.websocket.connection' implementation.
"""

# built-in
import asyncio

# third-party
from pytest import mark
import websockets

# module under test
from runtimepy.net.websocket.connection import WebsocketConnection

# internal
from tests.resources import SampleConnectionMixin


class SampleConnection(WebsocketConnection, SampleConnectionMixin):
    """A sample connection class."""


@mark.asyncio
async def test_websocket_server_basic():
    """Test basic interactions with a websocket server."""

    async def server_init(conn: SampleConnection) -> bool:
        """A sample handler."""

        conn.send_text("Hello, World!")
        conn.send_binary("Hello, World!".encode())
        return True

    async with websockets.server.serve(
        SampleConnection.server_handler(server_init), host="0.0.0.0", port=0
    ) as server:
        host = list(server.sockets)[0].getsockname()

        for _ in range(5):
            async with SampleConnection.client(
                f"ws://localhost:{host[1]}"
            ) as client:
                # Confirm that we receive two messages.
                await client.protocol.send(await client.protocol.recv())
                await client.protocol.send(await client.protocol.recv())


@mark.asyncio
async def test_websocket_connected_pair():
    """Test that we can create a connected pair."""

    async with SampleConnection.create_pair() as (conn1, conn2):
        conn1.send_text("Hello, World!")
        conn2.send_text("Hello, World!")
        conn1.send_text("stop")

        await asyncio.wait(
            [
                asyncio.create_task(conn1.process()),
                asyncio.create_task(conn2.process()),
            ],
            return_when=asyncio.ALL_COMPLETED,
        )
