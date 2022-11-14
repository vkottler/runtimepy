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


@mark.asyncio
async def test_websocket_server_basic():
    """Test basic interactions with a websocket server."""

    async def server_init(conn: WebsocketConnection) -> bool:
        """A sample handler."""

        conn.send_text("Hello, World!")
        conn.send_binary("Hello, World!".encode())
        return True

    async with websockets.server.serve(
        server_handler(server_init), host="0.0.0.0", port=0
    ) as server:
        host = list(server.sockets)[0].getsockname()

        # pylint: disable=no-member
        async with websockets.connect(  # type: ignore
            f"ws://localhost:{host[1]}"
        ) as client:
            # pylint: enable=no-member

            # Confirm that we receive two messages.
            await client.send(await client.recv())
            await client.send(await client.recv())
