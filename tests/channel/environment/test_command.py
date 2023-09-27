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


def test_channel_command_scalings():
    """Test commands against channels that have scalings."""

    env = ChannelEnvironment()

    env.int_channel(
        "4_20ma",
        commandable=True,
        scaling=[0.0, 3.81469727e-07],
        kind="uint16",
    )

    processor = ChannelCommandProcessor(env, getLogger(__name__))

    val = 0.0
    for _ in range(25):
        assert processor.command(f"set 4_20ma {val}")
        val += 0.01

    # Ensure that clamping works.
    assert processor.command("set 4_20ma 0.030")
    assert isclose(env.value("4_20ma"), 0.025, rel_tol=0.001)  # type: ignore


def test_channel_command_processor_basic():
    """Test basic interactions with the channel-command processor."""

    env = ChannelEnvironment()

    # Add some channels.
    env.int_channel("int1", commandable=True)
    env.bool_channel("bool1")
    env.float_channel("float1")

    env.bool_channel(
        "bool2",
        enum=env.enum("OnOff", "bool", {"on": True, "off": False}),
        commandable=True,
    )

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

    assert processor.command("get bool1")

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

    # Ensure boolean enums work.
    assert processor.command("set bool2 true")
    assert processor.command("set bool2 false")
    assert processor.command("set bool2 on")
    assert processor.command("set bool2 off")
    assert processor.command("toggle bool2")
    assert processor.command("toggle bool2")
