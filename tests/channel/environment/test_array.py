"""
Test the 'channel.environment.array' module.
"""

# module under test
from runtimepy.channel.environment import ChannelEnvironment

# internal
from tests.resources import resource


def test_channel_environment_array_basic():
    """
    Test that we can create channel and bit-field arrays using the channel
    environment.
    """

    env = ChannelEnvironment.load_directory(
        resource("channels", "environment", "sample")
    )

    array = env.array(
        [
            "bool.1",
            "bool.2",
            "bool.3",
            "int.1",
            "int.2",
            "int.3",
            "float.1",
            "float.2",
        ]
    )
    assert bytes(array.array)

    array = env.array(
        ["bool.1", "field0", "field1", "bool.2", "field5", "field6"]
    )
    assert bytes(array.array)
