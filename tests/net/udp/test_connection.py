"""
Test the 'net.udp.connection' module.
"""

# built-in
import asyncio
import socket

# third-party
from pytest import mark

# module under test
from runtimepy.net import get_free_socket_name
from runtimepy.net.connection import Connection
from runtimepy.net.udp.connection import UdpConnection


class SampleConnection(UdpConnection):
    """A sample connection class."""

    async def process_text(self, data: str) -> bool:
        """Process a text frame."""

        self.logger.info(data)
        return data != "stop"

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""
        return await self.process_text(data.decode())


async def close_after(conn: Connection, time: float) -> None:
    """Disable a connection after a delay."""
    await asyncio.sleep(time)
    conn.disable("timeout")


@mark.asyncio
async def test_udp_connection_basic():
    """Test basic interactions with a UDP connection."""

    conn1, conn2 = await SampleConnection.create_pair()
    assert conn1
    assert conn2

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

    # Sending to a local address that's not listening will trigger an error.
    conn3 = await SampleConnection.create_connection(
        remote_addr=get_free_socket_name(kind=socket.SOCK_DGRAM)
    )
    conn3.send_text("Hello!")
    await asyncio.wait(
        [
            asyncio.create_task(conn3.process()),
            asyncio.create_task(close_after(conn3, 0.01)),
        ],
        return_when=asyncio.ALL_COMPLETED,
    )

    conn4 = await SampleConnection.create_connection(
        local_addr=("localhost", 0)
    )
    assert conn4.remote_address is None
