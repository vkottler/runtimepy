"""
Test the 'net.websocket.server' implementation.
"""

# third-party
from pytest import mark
import websockets

# module under test
from runtimepy.net.websocket.server import WebsocketServer


@mark.asyncio
async def test_websocket_server_basic():
    """Test basic interactions with a websocket server."""

    async def handler(
        protocol: websockets.server.WebSocketServerProtocol,
    ) -> None:
        """A sample handler."""

        server = WebsocketServer(protocol)
        server.send_text("Hello, World!")
        server.send_binary("Hello, World!".encode())
        await server.process()

    async with websockets.server.serve(
        handler, host="0.0.0.0", port=0
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
