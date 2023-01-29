"""
Test the 'net.udp.connection' module.
"""

# third-party
from pytest import mark

# module under test
from runtimepy.net.udp.connection import UdpConnection


class SampleConnection(UdpConnection):
    """A sample connection class."""

    async def process_text(self, data: str) -> bool:
        """Process a text frame."""
        del data
        return True

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""
        del data
        return True


@mark.asyncio
async def test_udp_connection_basic():
    """Test basic interactions with a UDP connection."""

    conn1, conn2 = await SampleConnection.create_pair()
    assert conn1
    assert conn2
