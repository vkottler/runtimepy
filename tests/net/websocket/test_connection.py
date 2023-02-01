"""
Test the 'net.websocket.connection' implementation.
"""

# third-party
from pytest import mark
import websockets

# module under test
from runtimepy.net.websocket.connection import (
    WebsocketConnection,
    server_handler,
)


class SampleConnection(WebsocketConnection):
    """A sample connection class."""

    async def process_text(self, data: str) -> bool:
        """Process a text frame."""
        del data
        return True

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""
        del data
        return True


@mark.asyncio
async def test_websocket_server_basic():
    """Test basic interactions with a websocket server."""

    async def server_init(conn: SampleConnection) -> bool:
        """A sample handler."""

        conn.send_text("Hello, World!")
        conn.send_binary("Hello, World!".encode())
        return True

    async with websockets.server.serve(
        server_handler(server_init, SampleConnection), host="0.0.0.0", port=0
    ) as server:
        host = list(server.sockets)[0].getsockname()

        for _ in range(5):
            # pylint: disable=no-member
            async with websockets.connect(  # type: ignore
                f"ws://localhost:{host[1]}"
            ) as client:
                # pylint: enable=no-member

                # Confirm that we receive two messages.
                await client.send(await client.recv())
                await client.send(await client.recv())
