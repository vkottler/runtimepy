"""
Test the 'net.connection' module.
"""

# built-in
from logging import getLogger

# third-party
from pytest import mark, raises

# module under test
from runtimepy.net.connection import BinaryMessage, Connection


class SampleConnection(Connection):
    """A smaple conneciton class."""

    async def _send_text_message(self, data: str) -> None:
        """Send a text message."""
        print(data)

    async def _send_binay_message(self, data: BinaryMessage) -> None:
        """Send a binary message."""
        print(data)


@mark.asyncio
async def test_connection_basic():
    """Test basic interactions with a connection object."""

    conn = SampleConnection(getLogger(__name__))
    assert conn

    with raises(NotImplementedError):
        await conn.process_text("test")

    with raises(NotImplementedError):
        await conn.process_binary("test".encode())

    with raises(NotImplementedError):
        await conn._await_message()  # pylint: disable=protected-access
