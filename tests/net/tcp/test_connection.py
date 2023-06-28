"""
Test the 'net.tcp.connection' module.
"""

# built-in
import asyncio

# third-party
from pytest import mark

# module under test
from runtimepy.net import sockname
from runtimepy.net.manager import ConnectionManager

# internal
from tests.resources import SampleTcpConnection, release_after


@mark.asyncio
async def test_tcp_connection_basic():
    """Test basic interactions with a TCP connection."""

    conn1, conn2 = await SampleTcpConnection.create_pair()

    conn1.send_text("Hello!\n")
    conn2.send_text("Hello!\n")
    for idx in range(10):
        conn1.send_binary((str(idx) + "\n").encode())
        conn2.send_binary((str(idx) + "\n").encode())
    conn1.send_text("stop\n")
    conn2.send_text("stop\n")

    await asyncio.wait(
        [
            asyncio.create_task(conn1.process()),
            asyncio.create_task(conn2.process()),
        ],
        return_when=asyncio.ALL_COMPLETED,
    )


@mark.asyncio
async def test_tcp_connection_app():
    """Test the TCP connection's application interface."""

    manager = ConnectionManager()
    sig = asyncio.Event()
    host_queue: asyncio.Queue = asyncio.Queue()

    def app(conn: SampleTcpConnection) -> None:
        """A sample application callback."""
        assert conn

    def serve_cb(server) -> None:
        """Publish the server host."""
        host_queue.put_nowait(sockname(server.sockets[0]))

    async def connect() -> None:
        """Connect to the server a number of times."""

        # Wait for the server to start.
        host = await host_queue.get()

        for idx in range(10):
            try:
                conn = await SampleTcpConnection.create_connection(
                    host="localhost", port=host.port
                )

                if idx % 2 == 0:
                    conn.send_text("stop\n")

                # Allow the connection manager to manage this connection.
                await manager.queue.put(conn)

                if manager.num_connections:
                    manager.reset_metrics()
                    manager.poll_metrics()

            # Don't require every iteration to connection.
            except ConnectionRefusedError:
                pass

    # Continue making connections with the server and stop after some time, or
    # some number of connections?
    await asyncio.wait(
        [
            asyncio.create_task(x)
            for x in [
                release_after(sig, 0.1),
                connect(),
                SampleTcpConnection.app(
                    sig,
                    callback=app,
                    serving_callback=serve_cb,
                    port=0,
                    manager=manager,
                ),
            ]
        ],
        return_when=asyncio.ALL_COMPLETED,
    )

    # For code coverage.
    await SampleTcpConnection.app(sig, port=0)
