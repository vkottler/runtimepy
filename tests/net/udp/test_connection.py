"""
Test the 'net.udp.connection' module.
"""

# built-in
import asyncio
import socket

# third-party
from pytest import mark

# module under test
from runtimepy.net import get_free_socket, get_free_socket_name, normalize_host
from runtimepy.net.connection import Connection

# internal
from tests.resources import SampleUdpConnection


class SampleConnectionInitFail(SampleUdpConnection):
    """Overrides the connection initialization to fail."""

    async def async_init(self) -> bool:
        """A runtime initialization routine (executes during 'process')."""
        return False


@mark.asyncio
async def test_udp_connection_init_fail():
    """Test basic interactions with a UDP connection."""

    conn1, conn2 = await SampleConnectionInitFail.create_pair()

    # Should complete immediately.
    await asyncio.wait(
        [
            asyncio.create_task(conn1.process()),
            asyncio.create_task(conn2.process()),
        ],
        return_when=asyncio.ALL_COMPLETED,
    )


async def close_after(conn: Connection, time: float) -> None:
    """Disable a connection after a delay."""
    await asyncio.sleep(time)
    conn.disable("timeout")


@mark.asyncio
async def test_udp_connection_basic():
    """Test basic interactions with a UDP connection."""

    conn1, conn2 = await SampleUdpConnection.create_pair()

    assert conn1.socket
    assert conn2.socket

    conn1.send_text("Hello!")
    conn2.send_text("Hello!")
    for idx in range(10):
        conn1.send_binary(str(idx).encode())
        conn2.send_binary(str(idx).encode())
    conn1.send_text("stop")
    conn2.send_text("stop")

    await asyncio.wait(
        [
            asyncio.create_task(conn1.process()),
            asyncio.create_task(conn2.process()),
        ],
        return_when=asyncio.ALL_COMPLETED,
    )


@mark.asyncio
async def test_udp_connection_restart():
    """Test that a UDP connection can be restarted."""

    host = "127.0.0.1"
    port = get_free_socket_name(
        local=normalize_host(host), kind=socket.SOCK_DGRAM
    ).port

    server = await SampleUdpConnection.create_connection(
        local_addr=(host, port)
    )

    # Start the server.
    task = asyncio.create_task(server.process())

    client = await SampleUdpConnection.create_connection(
        remote_addr=(host, port)
    )

    # Run the connection for a bit.
    await client.process(disable_time=0.1)

    # Run the connection again (triggering a restart).
    await client.process(disable_time=0.1)

    # Confirm the connection did restart.
    assert client.env.value("restarts") == 1

    # Stop the server.
    server.disable("end test")
    await task


@mark.asyncio
async def test_udp_connection_endpoint_down():
    """Test sending data to an endpoint that is closed."""

    # Create a socket so that a connection can be established.
    sock = get_free_socket(kind=socket.SOCK_DGRAM)

    # Sending to a local address that's not listening will trigger an error.
    conn3 = await SampleUdpConnection.create_connection(
        remote_addr=("localhost", sock.getsockname()[1])
    )

    sock.close()
    conn3.send_text("Hello!")

    await conn3.process()

    # Try restarting.
    await conn3.process(disable_time=0.01)


@mark.asyncio
async def test_udp_connection_no_endpoint():
    """Test that we can send data without connecting the underlying socket."""

    conn4 = await SampleUdpConnection.create_connection(
        local_addr=("localhost", 0)
    )
    assert conn4.remote_address is None
    conn4.sendto("Hello!".encode(), conn4.local_address)
    await asyncio.wait(
        [
            asyncio.create_task(conn4.process()),
            asyncio.create_task(close_after(conn4, 0.01)),
        ],
        return_when=asyncio.ALL_COMPLETED,
    )
