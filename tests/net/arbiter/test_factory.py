"""
Test the 'net.arbiter.factory' method.
"""

# third-party
from pytest import raises

# module under test
from runtimepy.net.arbiter.config.util import list_adder
from runtimepy.net.arbiter.factory import ConnectionFactory

# internal
from tests.resources import run_async_test


async def connection_factory_basic(factory: ConnectionFactory) -> None:
    """Test basic interactions with the connection factory base class."""

    with raises(NotImplementedError):
        await factory.client("test")

    with raises(NotImplementedError):
        await factory.server_task(None, None, None)  # type: ignore


def test_connection_factory_basic():
    """Test basic interactions with the connection factory base class."""

    # For coverage.
    list_adder([], "a", front=False)

    run_async_test(connection_factory_basic(ConnectionFactory()))
