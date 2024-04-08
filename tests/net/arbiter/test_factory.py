"""
Test the 'net.arbiter.factory' method.
"""

# third-party
from pytest import mark, raises

# module under test
from runtimepy.net.arbiter.config.util import list_adder
from runtimepy.net.arbiter.factory import ConnectionFactory


@mark.asyncio
async def test_connection_factory_basic():
    """Test basic interactions with the connection factory base class."""

    # For coverage.
    list_adder([], "a", front=False)

    factory = ConnectionFactory()

    with raises(NotImplementedError):
        await factory.client("test")

    with raises(NotImplementedError):
        await factory.server_task(None, None, None)  # type: ignore
