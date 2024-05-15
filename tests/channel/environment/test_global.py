"""
Test interactions with global environments.
"""

# built-in
from contextlib import ExitStack, contextmanager
import logging
from typing import Iterator

# module under test
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.channel.environment.command import GlobalEnvironment
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
)
from runtimepy.channel.registry import ParsedEvent


def sample_env(name: str) -> ChannelCommandProcessor:
    """Create a sample channel environment."""

    env = ChannelEnvironment()

    env.int_channel("null.uint32", commandable=True)
    env.int_channel("null.int32", kind="int32", commandable=True)
    env.bool_channel("null.bool", commandable=True)
    env.float_channel("null.float", commandable=True)
    env.float_channel("null.double", kind="double", commandable=True)

    return ChannelCommandProcessor(env, logging.getLogger(name))


def poke_sample_env(env: ChannelEnvironment) -> None:
    """Change some values in the sample environment."""

    env.set("null.uint32", 0)
    env.set("null.uint32", 1)

    env.set("null.int32", 1)
    env.set("null.int32", -1)

    env.set("null.bool", False)
    env.set("null.bool", True)

    env.set("null.float", 1.0)
    env.set("null.float", -1.0)

    env.set("null.double", 1.0)
    env.set("null.double", -1.0)


ENVS = ["a", "b", "c"]


@contextmanager
def global_test_env() -> Iterator[GlobalEnvironment]:
    """Create a global environment configured for testing purposes."""

    with ExitStack() as stack:
        envs = stack.enter_context(GlobalEnvironment.temporary())

        for name in ENVS:
            envs.register(name, sample_env(name))

        yield envs


def test_global_environment_basic():
    """Test simple interactions with a global environment."""

    with global_test_env() as envs:
        # Write output.
        with envs.event_telemetry_output() as channels:
            for env, _ in channels:
                poke_sample_env(envs[env].env)

        # Create a new environment from the output and verify the expected
        # events.
        new_envs = GlobalEnvironment.from_root(envs.valid_root)

        for name in ENVS:
            events = ParsedEvent.by_channel(new_envs.read_event_stream(name))
            assert len(events["null.uint32"]) == 2
            assert len(events["null.int32"]) == 3
