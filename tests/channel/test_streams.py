"""
Test data-streaming capabilities of channel registries.
"""

# third-party
from vcorelib.paths.context import tempfile

# module under test
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.mapping import DEFAULT_PATTERN


def test_channel_registry_streams_basic():
    """Test basic interactions with a streaming chanel events."""

    env = ChannelEnvironment()
    assert env.int_channel("a")
    assert env.int_channel("b")
    assert env.int_channel("c")

    assert len(list(env.channels.search(DEFAULT_PATTERN))) == 3

    with tempfile() as path:
        with path.open("wb") as path_fd:
            with env.channels.registered(path_fd):
                assert env.channels["a"].raw.callbacks

                env.set("a", 1)
                env.set("b", 2)
                env.set("c", 3)

        # Open for reading and verify events.
        with path.open("rb") as path_fd:
            events = list(env.parse_event_stream(path_fd))

            assert len(events) == 6

            assert events[0].name == "a"
            assert events[0].value == 0
            assert events[1].name == "b"
            assert events[1].value == 0
            assert events[2].name == "c"
            assert events[2].value == 0

            assert events[3].name == "a"
            assert events[3].value == 1
            assert events[4].name == "b"
            assert events[4].value == 2
            assert events[5].name == "c"
            assert events[5].value == 3
