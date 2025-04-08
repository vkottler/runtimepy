"""
Test the 'codec.protocol' module.
"""

# built-in
from copy import copy
from io import BytesIO
from json import load
from logging import getLogger

# module under test
from runtimepy.codec.protocol import Protocol, ProtocolFactory
from runtimepy.codec.protocol.base import FieldSpec
from runtimepy.enum.registry import EnumRegistry
from runtimepy.primitives import Uint32
from runtimepy.primitives.serializable import PrefixedChunk

# internal
from tests.resources import resource

LOG = getLogger(__name__)


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


class SampleA(ProtocolFactory):
    """A sample protocol implementation."""

    protocol = Protocol(EnumRegistry())

    @classmethod
    def initialize(cls, protocol: Protocol) -> None:
        """Initialize this protocol."""

        protocol.add_field("a", "uint32")
        protocol.add_field("b", "float")
        protocol.add_field("c_array", "uint32", array_length=6)


class SampleB(ProtocolFactory):
    """A sample protocol implementation."""

    protocol = Protocol(EnumRegistry())

    @classmethod
    def initialize(cls, protocol: Protocol) -> None:
        """Initialize this protocol."""

        protocol.add_field("a_single", serializable=SampleA.instance())
        protocol.add_field(
            "a_array", serializable=SampleA.instance(), array_length=2
        )
        protocol.add_field("c", "int32")


class SampleC(ProtocolFactory):
    """A sample protocol implementation."""

    protocol = Protocol(EnumRegistry())

    @classmethod
    def initialize(cls, protocol: Protocol) -> None:
        """Initialize this protocol."""

        protocol.add_field("a_single", serializable=SampleA.instance())
        protocol.add_field(
            "a_array", serializable=SampleA.instance(), array_length=2
        )
        protocol.add_field("b_single", serializable=SampleB.instance())
        protocol.add_field(
            "b_array", serializable=SampleB.instance(), array_length=2
        )
        protocol.add_field("d", "bool")
        protocol.add_field("e", "bool")
        protocol.add_field("f", "bool")
        protocol.add_field("g", "bool")


def dump_protocol_info(inst: Protocol) -> None:
    """Dump information about a protocol."""

    LOG.info(inst.resolve_alias())
    LOG.info(inst)
    LOG.info("%d: %s", inst.length(), inst.length_trace())


def test_protocol_nested():
    """Test basic interactions with nested protocol objects."""

    inst_a = SampleA.instance()
    inst_b = SampleB.instance()
    inst_c = SampleC.instance()

    assert inst_a.length() == 32
    assert len(inst_a.chain_bytes()) == 32
    assert inst_b.length() == 100
    assert len(inst_b.chain_bytes()) == 100
    assert inst_c.length() == 400
    assert len(inst_c.chain_bytes()) == 400

    inst_a.randomize()
    dump_protocol_info(inst_a)

    new_inst = SampleA.instance()
    assert new_inst != inst_a
    new_inst.update_with(inst_a)
    assert new_inst == inst_a

    inst_b.randomize()
    dump_protocol_info(inst_b)

    new_inst = SampleB.instance()
    assert new_inst != inst_b
    new_inst.update_with(inst_b)
    assert new_inst == inst_b

    inst_c.randomize()
    dump_protocol_info(inst_c)

    new_inst = SampleC.instance()
    assert new_inst != inst_c
    new_inst.update_with(inst_c)
    assert new_inst == inst_c
