"""
Test the 'net.udp.connection' module.
"""

# built-in
import asyncio
import socket

# third-party
from pytest import mark

# module under test
from runtimepy.net import get_free_socket
from runtimepy.net.connection import Connection
from runtimepy.net.udp.connection import UdpConnection

# internal
from tests.resources import SampleConnectionMixin


class SampleConnection(UdpConnection, SampleConnectionMixin):
    """A sample connection class."""


async def close_after(conn: Connection, time: float) -> None:
    """Disable a connection after a delay."""
    await asyncio.sleep(time)
    conn.disable("timeout")


@mark.asyncio
async def test_udp_connection_basic():
    """Test basic interactions with a UDP connection."""

    conn1, conn2 = await SampleConnection.create_pair()

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
async def test_udp_connection_endpoint_down():
    """Test sending data to an endpoint that is closed."""

    # Create a socket so that a connection can be established.
    sock = get_free_socket(kind=socket.SOCK_DGRAM)

    # Sending to a local address that's not listening will trigger an error.
    conn3 = await SampleConnection.create_connection(
        remote_addr=("localhost", sock.getsockname()[1])
    )

    sock.close()
    conn3.send_text("Hello!")

    await asyncio.wait(
        [
            asyncio.create_task(conn3.process()),
            asyncio.create_task(close_after(conn3, 0.01)),
        ],
        return_when=asyncio.ALL_COMPLETED,
    )


@mark.asyncio
async def test_udp_connection_no_endpoint():
    """Test that we can send data without connecting the underlying socket."""

    conn4 = await SampleConnection.create_connection(
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
