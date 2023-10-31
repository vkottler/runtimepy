"""
Test the 'net.tcp.connection' module.
"""

# built-in
import asyncio

# third-party
from pytest import mark

# module under test
from runtimepy.net import (
    ExponentialBackoff,
    get_free_socket_name,
    normalize_host,
    sockname,
)
from runtimepy.net.manager import ConnectionManager

# internal
from tests.resources import SampleTcpConnection, release_after


@mark.asyncio
async def test_tcp_connection_basic():
    """Test basic interactions with a TCP connection."""

    async with SampleTcpConnection.create_pair() as (conn1, conn2):
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
async def test_tcp_connection_restart():
    """Test that a TCP connection can be restarted."""

    host = "127.0.0.1"
    port = get_free_socket_name(local=normalize_host(host)).port

    async with SampleTcpConnection.serve(host=host, port=port):
        client = await SampleTcpConnection.create_connection(
            host=host, port=port
        )

        # Run the connection for a bit.
        await client.process(disable_time=0.1)

        # Run the connection again (triggering a restart).
        await client.process(disable_time=0.1)

        # Confirm the connection did restart.
        assert client.env.value("restarts") == 1

    # Trigger another restart.
    await asyncio.sleep(0.01)
    await client.process(backoff=ExponentialBackoff(max_tries=3))
    await client.process(backoff=ExponentialBackoff(max_tries=0))


@mark.asyncio
async def test_tcp_connection_manager_auto_restart():
    """
    Test that a connection manager can automatically restart TCP connections.
    """

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

        conn = await SampleTcpConnection.create_connection(
            host="localhost", port=host.port
        )

        # Allow the connection manager to manage this connection.
        await manager.queue.put(conn)

        await conn.initialized.wait()

        # Enable connection restart.
        conn.env.set("auto_restart", True)

        # Disable the connection.
        conn.send_text("stop\n")
        await conn.exited.wait()

        # Wait for re-connect.
        await conn.initialized.wait()

        # Confirm the connection did restart.
        assert conn.env.value("restarts") == 1

        # End test.
        conn.env.set("auto_restart", False)
        conn.send_text("stop\n")
        await conn.exited.wait()
        sig.set()

    await asyncio.wait(
        [
            asyncio.create_task(x)
            for x in [
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
                if not sig.is_set():
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
                release_after(sig, 0.2),
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
