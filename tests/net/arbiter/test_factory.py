"""
Test the 'net.arbiter.factory' method.
"""

# third-party
from pytest import mark, raises

# module under test
from runtimepy.net.arbiter.factory import ConnectionFactory


@mark.asyncio
async def test_connection_factory_basic():
    """Test basic interactions with the connection factory base class."""

    factory = ConnectionFactory()

    with raises(NotImplementedError):
        await factory.client()

    with raises(NotImplementedError):
        await factory.server_task(None, None)  # type: ignore
