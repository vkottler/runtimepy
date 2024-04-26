"""
Test the 'net.udp.queue' module.
"""

# built-in
import asyncio

# third-party
from pytest import mark

# module under test
from runtimepy.net.udp import QueueUdpConnection


@mark.asyncio
async def test_udp_queue_basic():
    """Test basic interactions with a UDP queue connection."""

    conn1, conn2 = await QueueUdpConnection.create_pair()

    sig = asyncio.Event()

    tasks = [
        asyncio.create_task(conn1.process(stop_sig=sig)),
        asyncio.create_task(conn2.process(stop_sig=sig)),
    ]

    msg = "Hello, world!"
    for conn in [conn1, conn2]:
        conn.send_text(msg)

    for conn in [conn1, conn2]:
        assert (await conn.datagrams.get())[0].decode() == msg

    # Clean up.
    sig.set()
    for task in tasks:
        await task
