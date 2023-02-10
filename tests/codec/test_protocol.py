"""
Test the 'codec.protocol' module.
"""

# built-in
from copy import copy
from io import BytesIO
from json import load

# module under test
from runtimepy.codec.protocol import Protocol
from runtimepy.codec.protocol.base import FieldSpec
from runtimepy.enum.registry import EnumRegistry

# internal
from tests.resources import resource


def test_protocol_basic():
    """Test basic interactions with protocol objects."""

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