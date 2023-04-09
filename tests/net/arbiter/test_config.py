"""
Test the 'net.arbiter.config' module.
"""

# third-party
from pytest import mark

# module under test
from runtimepy.net.arbiter import ConnectionArbiter

# internal
from tests.resources import resource


@mark.asyncio
async def test_connection_arbiter_config_basic():
    """Test basic loading of the connection-arbiter config."""

    arbiter = ConnectionArbiter()

    # Register clients and servers from the config.
    await arbiter.load_config(resource("connection_arbiter", "basic.yaml"))

    assert await arbiter.app() == 0
