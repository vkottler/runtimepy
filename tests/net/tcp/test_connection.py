"""
Test the 'net.tcp.connection' module.
"""

# built-in
import asyncio

# third-party
from pytest import mark

# module under test
from runtimepy.net.tcp.connection import TcpConnection

# internal
from tests.resources import SampleConnectionMixin


class SampleConnection(TcpConnection, SampleConnectionMixin):
    """A sample connection class."""


@mark.asyncio
async def test_tcp_connection_basic():
    """Test basic interactions with a TCP connection."""

    conn1, conn2 = await SampleConnection.create_pair()

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


async def release_after(sig: asyncio.Event, time: float) -> None:
    """Disable a connection after a delay."""
    await asyncio.sleep(time)
    sig.set()


@mark.asyncio
async def test_tcp_connection_app():
    """Test the TCP connection's application interface."""

    sig = asyncio.Event()

    # Continue making connections with the server and stop after some time, or
    # some number of connections?
    await asyncio.wait(
        [release_after(sig, 0.01), SampleConnection.app(sig, port=0)],
        return_when=asyncio.ALL_COMPLETED,
    )
