"""
Test the 'channel.environment.create' module.
"""

# module under test
from runtimepy.channel.environment import ChannelEnvironment


def test_channel_environment_create_basic():
    """Test basic channel and enumeration creation scenarios."""

    env = ChannelEnvironment()

    enum = env.enum("sample_enum", "bool", items={"on": True, "off": False})

    result = env.channel("sample_channel", "bool", enum=enum)
    assert result
