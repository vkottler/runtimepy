"""
Test the 'channel.environment.file' module.
"""

# third-party
from vcorelib.io import ARBITER

# module under test
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.channel.environment.sample import sample_env

# internal
from tests.resources import resource


def test_channel_environment_load_json():
    """
    Verify that we can load a channel environment from a single dictionary.
    """

    env = ChannelEnvironment.load_json(
        ARBITER.decode_directory(  # type: ignore
            resource("channels", "environment", "sample"), require_success=True
        ).data
    )
    assert env

    new_env = ChannelEnvironment.load_json(env.export_json())
    assert new_env.channels == env.channels

    assert ChannelEnvironment.load_json(sample_env().export_json())
