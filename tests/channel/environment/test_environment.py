"""
Test the 'channel.environment' module.
"""

# built-in
from io import SEEK_CUR, BytesIO
from tempfile import TemporaryDirectory

# third-party
from pytest import raises

# module under test
from runtimepy.channel.environment import ChannelEnvironment

# internal
from tests.resources import resource


def verify_values(env: ChannelEnvironment) -> None:
    """Verify initial channel values."""

    assert env.channels.names.name(1) == "bool.1"

    # Verify values.
    assert env.value("bool.1") is True
    assert env.value("bool.2") == "on"
    assert env.value("bool.3") == "off"
    assert env.value("int.1") == 5
    assert env.value("int.2", resolve_enum=False) == 4
    assert env.value("int.3") == "error"
    assert env.value("float.1") == 0.0
    assert env.value("float.2") == 1.0

    env.set("bool.2", 0)
    assert env.value("bool.2") == "off"
    env.set("bool.2", 1)
    assert env.value("bool.2") == "on"

    assert env.get_int("int.2")[0].is_enum

    assert env.value("field4") == "wait"

    assert env.value("field0") == 1

    assert env.value("field1") == "off"
    env.set("field1", 1)
    assert env.value("field1") == "on"


def verify_missing_keys(env: ChannelEnvironment) -> None:
    """Verify behavior when using incorrect registry keys."""

    int_chan, enum = env.get_int("int.2")
    assert int_chan
    assert enum is not None

    with raises(KeyError):
        assert enum.get_str(10)
    with raises(KeyError):
        assert enum.get_int("bad")

    with raises(ValueError):
        env.set("int.1", "off")

    with raises(KeyError):
        assert env["bad_channel"]

    with raises(KeyError):
        assert env.get_int("bool.1")
    with raises(KeyError):
        assert env.get_float("bool.1")
    with raises(KeyError):
        assert env.get_bool("int.1")


def verify_bitfields(env: ChannelEnvironment) -> None:
    """Verify behavior of the bit-fields manager."""

    assert env.fields.values()["field4"] == "wait"

    with raises(KeyError):
        assert env.fields["field5"]

    with raises(KeyError):
        assert env.fields.get_flag("field4")

    assert env.fields.get_flag("field1").get() is True

    assert env.fields[20].name == "field4"


def test_channel_environment_basic():
    """Test basic interactions with a channel environment."""

    env = ChannelEnvironment()
    env = ChannelEnvironment.load_directory(
        resource("channels", "environment", "sample")
    )
    verify_values(env)
    verify_bitfields(env)

    # Verify exporting and re-importing the environment.
    with TemporaryDirectory() as tmpdir:
        env.export_directory(tmpdir)
        assert env == ChannelEnvironment.load_directory(tmpdir)

    assert env.get_bool("bool.1") is not None
    assert env.get_bool(1) is not None

    chan = env.get_bool("bool.1")[0]
    chan.raw.set()
    assert bool(chan)
    chan.raw.toggle()
    assert not bool(chan)
    chan.raw.clear()
    assert not bool(chan)

    assert str(chan)

    test_val = False
    assert chan.raw == test_val
    assert chan.raw == chan.raw

    size = 1
    chan.raw.set()
    with BytesIO() as stream:
        # Verify we encode 'true'.
        assert chan.raw.to_stream(stream) == size
        stream.seek(-1 * size, SEEK_CUR)
        chan.raw.from_stream(stream)
        assert chan

        # Change the value.
        chan.raw.toggle()

        # Verify we encode 'false'.
        assert chan.raw.to_stream(stream) == size
        stream.seek(-1 * size, SEEK_CUR)
        chan.raw.from_stream(stream)
        assert not chan

    assert bytes(chan.raw)

    _, enum = env.get_bool("bool.2")
    assert enum is not None
    with raises(KeyError):
        assert enum.get_bool("open")

    assert env.get_float("float.1") is not None
    assert env.get_float(7) is not None
    assert env.get_float(7).raw == 0.0

    assert env.get_int("int.1") is not None
    assert env.get_int(4) is not None

    verify_missing_keys(env)
