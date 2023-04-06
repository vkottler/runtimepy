"""
Test the 'net.websocket.connection' implementation.
"""

# built-in
import asyncio
from contextlib import AsyncExitStack

# third-party
from pytest import mark
from websockets.server import WebSocketServer

# module under test
from runtimepy.net import sockname
from runtimepy.net.websocket.connection import WebsocketConnection

# internal
from tests.resources import SampleConnectionMixin, release_after


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

    async with SampleConnection.serve(
        server_init, host="0.0.0.0", port=0
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
                asyncio.create_task(conn2.process()),
                asyncio.create_task(conn1.process()),
            ],
            return_when=asyncio.ALL_COMPLETED,
        )


@mark.asyncio
async def test_websocket_server_app():
    """Test that we can set up a websocket-server application."""

    server_queue: asyncio.Queue = asyncio.Queue()
    sig = asyncio.Event()

    async def conn_init(conn: SampleConnection) -> bool:
        """A sample handler."""
        assert conn
        return True

    def serve_cb(server: WebSocketServer) -> None:
        """Publish the server host."""
        server_queue.put_nowait(sockname(list(server.sockets)[0]))

    async def connect() -> None:
        """Connect to the server a number of times."""

        async with AsyncExitStack() as stack:
            # Wait for the server to start.
            host = await server_queue.get()

            conns = []
            for idx in range(20):
                try:
                    conn = await stack.enter_async_context(
                        SampleConnection.client(f"ws://localhost:{host.port}")
                    )
                    conns.append(conn)

                    if idx % 2 == 0:
                        conn.send_text("stop")
                except (ConnectionRefusedError, OSError):
                    pass

            # Wait for connections to close.
            assert conns
            await asyncio.wait(
                [asyncio.create_task(conn.process()) for conn in conns],
                return_when=asyncio.ALL_COMPLETED,
            )

    await asyncio.wait(
        [
            asyncio.create_task(x)
            for x in [
                connect(),
                release_after(sig, 0.1),
                SampleConnection.app(
                    sig,
                    conn_init,
                    serving_callback=serve_cb,
                    host="0.0.0.0",
                    port=0,
                ),
            ]
        ],
        return_when=asyncio.ALL_COMPLETED,
    )
