"""
Test the 'codec.protocol' module.
"""

# built-in
from copy import copy
from io import BytesIO
from json import load

# module under test
from runtimepy.codec.protocol import Protocol, ProtocolFactory
from runtimepy.codec.protocol.base import FieldSpec
from runtimepy.enum.registry import EnumRegistry
from runtimepy.primitives import Uint32
from runtimepy.primitives.serializable import PrefixedChunk

# internal
from tests.resources import resource


class SampleProtocol(ProtocolFactory):
    """A sample protocol implementation."""

    protocol = Protocol(EnumRegistry())

    @classmethod
    def initialize(cls, protocol: Protocol) -> None:
        """Initialize this protocol."""

        protocol.add_field("test1", "uint8")


class StartsWithChunk(ProtocolFactory):
    """A sample protocol implementation."""

    protocol = Protocol(EnumRegistry())

    @classmethod
    def initialize(cls, protocol: Protocol) -> None:
        """Initialize this protocol."""

        protocol.add_serializable("node_name", PrefixedChunk(Uint32()))
        protocol.add_field("a", "uint32")
        protocol.add_field("b", "uint32")
        protocol.add_field("c", "uint32")


def test_protocol_starts_with_serializable():
    """Test that protocols that start with serializables work."""

    proto = StartsWithChunk.instance()

    proto["a"] = 1000
    proto["b"] = 2000
    proto["c"] = 3000

    proto["node_name"] = "Hello, world!"
    assert proto["node_name"] == "Hello, world!"
    assert proto["a"] == 1000

    new_inst = StartsWithChunk.instance()

    # Serialize and then de-serialize.
    with BytesIO() as ostream:
        size = proto.to_stream(ostream)
        data = ostream.getvalue()
        assert data
        with BytesIO(data) as istream:
            assert new_inst.from_stream(istream) == size

    assert new_inst["node_name"] == "Hello, world!"
    assert new_inst["a"] == 1000
    assert new_inst["b"] == 2000
    assert new_inst["c"] == 3000

    assert proto.length() == new_inst.length()


def test_protocol_basic():
    """Test basic interactions with protocol objects."""

    assert SampleProtocol.singleton() is SampleProtocol.singleton()

    assert SampleProtocol.instance().length() == 1
    assert SampleProtocol.instance().length() == 1

    proto = Protocol(
        EnumRegistry.decode(resource("enums", "sample_enum.yaml"))
    )

    proto.add_field("test1", "uint8")

    # Add bit fields.
    with proto.add_bit_fields() as fields:
        fields.flag("flag1", enum="bool1")
        fields.flag("flag2")

    proto.add_field("test2", "uint8", enum="int1")

    proto["test2"] = "b"
    assert proto["test2"] == "b"

    proto["flag1"] = "valve_open"
    assert proto["flag1"] == "valve_open"

    proto["flag2"] = True
    assert proto["flag2"] is True

    new_proto = copy(proto)
    assert new_proto

    proto["test1"] = 40
    new_proto["test1"] = 50

    assert proto["test1"] == 40
    assert new_proto["test1"] == 50

    assert FieldSpec("test", "uint8", enum="int1").asdict()

    new_proto = Protocol.import_json(proto.export_json())
    assert new_proto["test1"] == 40
    assert proto["flag1"] == "valve_open"

    with BytesIO() as stream:
        assert proto.write_meta(stream)
        stream.seek(0)
        assert Protocol.import_json(load(stream))

    assert str(proto)

    # Create a string serializable.
    string = PrefixedChunk.create()
    assert string.length() == 2
    assert string.update_str("abc") == 5

    # Add the string to the end and confirm the size update.
    curr = proto.length()
    proto.add_field("string", serializable=string)
    assert proto.length() == curr + 5

    # Should be the same size.
    assert copy(proto).length() == proto.length()
