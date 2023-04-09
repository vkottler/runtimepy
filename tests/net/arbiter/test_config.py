"""
Test the 'net.arbiter.config' module.
"""

# third-party
from pytest import mark

# module under test
from runtimepy.net.arbiter.config import ConnectionArbiterConfig

# internal
from tests.net.arbiter import get_test_arbiter
from tests.resources import resource


@mark.asyncio
async def test_connection_arbiter_config_basic():
    """Test basic loading of the connection-arbiter config."""

    arbiter = get_test_arbiter()

    # Register clients and servers from the config.
    await arbiter.process_config(
        ConnectionArbiterConfig.decode(
            resource("connection_arbiter", "basic.yaml")
        )
    )

    assert await arbiter.app() == 0
