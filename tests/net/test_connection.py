"""
Test the 'net.connection' module.
"""

# built-in
from logging import getLogger

# third-party
from pytest import mark, raises

# module under test
from runtimepy.net.connection import Connection


@mark.asyncio
async def test_connection_basic():
    """Test basic interactions with a connection object."""

    conn = Connection(getLogger(__name__))
    assert conn

    with raises(NotImplementedError):
        await conn.process_text("test")

    with raises(NotImplementedError):
        await conn.process_binary("test".encode())

    with raises(NotImplementedError):
        await conn._await_message()  # pylint: disable=protected-access

    with raises(NotImplementedError):
        await conn._send_text_message(  # pylint: disable=protected-access
            "test"
        )

    with raises(NotImplementedError):
        await conn._send_binay_message(  # pylint: disable=protected-access
            "test".encode()
        )

    conn.disable("testing")
    with raises(NotImplementedError):
        await conn.process()
