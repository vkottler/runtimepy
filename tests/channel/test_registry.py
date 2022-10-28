"""
Test the 'channel.registry' module.
"""

# module under test
from runtimepy.channel.registry import ChannelRegistry

# internal
from tests.resources import resource


def test_channel_registry_basic():
    """Test basic interactions with a channel registry."""

    registry = ChannelRegistry.decode(
        resource("channels", "sample_registry.yaml")
    )
    assert registry
