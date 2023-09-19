"""
Test the 'channel.environment.command' module.
"""

# built-in
from argparse import Namespace
from logging import getLogger
from math import isclose
from typing import Optional

# module under test
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.channel.environment.command import (
    ChannelCommandProcessor,
    FieldOrChannel,
)


def sample_command_hook(
    args: Namespace, channel: Optional[FieldOrChannel]
) -> None:
    """Perform extra command actions."""

    del args
    del channel


def test_channel_command_processor_basic():
    """Test basic interactions with the channel-command processor."""

    env = ChannelEnvironment()

    # Add some channels.
    env.int_channel("int1", commandable=True)
    env.bool_channel("bool1")
    env.float_channel("float1")

    processor = ChannelCommandProcessor(env, getLogger(__name__))
    processor.hooks.append(sample_command_hook)

    processor.parser.exit(message="null")

    assert processor.get_suggestion("set in") is not None
    assert processor.get_suggestion("set not_a_channel") is None

    result = processor.command("asdf")
    assert not result
    assert str(result)
    assert not processor.command("help")

    assert not env.value("bool1")
    assert not processor.command("toggle bool1")
    assert processor.command("toggle -f bool1")
    assert not processor.command("toggle int1")
    assert not processor.command("toggle asdf")
    assert env.value("bool1")

    assert env.value("int1") == 0
    assert not processor.command("set int1")
    assert processor.command("set int1 42")
    assert not processor.command("set int1 asdf")
    assert env.value("int1") == 42

    assert env.value("float1") == 0
    assert processor.command("set float1 42 -f")
    assert isclose(env.value("float1"), 42)  # type: ignore
    assert processor.command("set float1 -101.5 -f")
    assert isclose(env.value("float1"), -101.5)  # type: ignore

    assert processor.command("set bool1 true -f")
    assert env.value("bool1")

    assert not processor.command("set bool1 ttrue -f")

    assert processor.command("set bool1 false -f")
    assert not env.value("bool1")
