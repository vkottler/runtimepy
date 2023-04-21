"""
Test the 'net.stream.connection' module.
"""

# internal
import os

# third-party
from pytest import mark

# module under test
from runtimepy.net.stream import EchoStreamConnection


@mark.asyncio
async def test_echo_stream_connection_basic():
    """Test basic interactions with a simple echo stream."""

    conn = await EchoStreamConnection.create()
    await conn.process()


@mark.asyncio
async def old_method():
    """Test basic interactions with a simple echo stream."""

    read, write = os.pipe()

    pid = os.fork()

    # Parent.
    if pid:
        os.close(write)

        conn = await EchoStreamConnection.create(read=os.fdopen(read, "rb"))
        await conn.process()

    # Child.
    else:
        os.close(read)

        stream = os.fdopen(write)
        for idx in range(100):
            stream.write(f"{idx}\n")
        os.close(write)
