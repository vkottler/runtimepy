"""
Test the 'channel.environment.create' module.
"""

# built-in
import logging

# module under test
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
)
from runtimepy.primitives import Uint8
from runtimepy.primitives.field import BitField


def test_channel_environment_create_basic():
    """Test basic channel and enumeration creation scenarios."""

    env = ChannelEnvironment()

    enum = env.enum("sample_enum", "bool", items={"on": True, "off": False})

    result = env.channel(
        "sample_channel", "bool", enum=enum, description="A sample channel."
    )
    assert result

    assert len(list(env.search_names("sample_channel", exact=True))) == 1

    env.age_ns("sample_channel")

    name = "test_field"
    underlying = Uint8()

    assert env.add_field(BitField(name, underlying, 0, 1, commandable=True))
    env.finalize()

    assert not env.value("test_field")

    env.set("test_field", True)
    assert env.value("test_field")
    assert underlying.value == 1

    proc = ChannelCommandProcessor(env, logging.getLogger(__name__))

    assert proc.command("set test_field true")
    assert underlying.value == 1
    env.age_ns("test_field")

    assert proc.command("set test_field false")
    assert underlying.value == 0

    assert proc.command("toggle test_field")
    assert underlying.value == 1

    assert proc.command("toggle test_field")
    assert underlying.value == 0

    assert proc.command("set test_field 1")
    assert underlying.value == 1

    assert proc.command("set test_field 0")
    assert underlying.value == 0
