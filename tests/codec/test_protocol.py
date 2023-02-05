"""
Test the 'codec.protocol' module.
"""

# module under test
from runtimepy.codec.protocol import Protocol
from runtimepy.enum.registry import EnumRegistry

# internal
from tests.resources import resource


def test_protocol_basic():
    """Test basic interactions with protocol objects."""

    proto = Protocol(
        EnumRegistry.decode(resource("enums", "sample_enum.yaml"))
    )

    proto.add_field("test1", "uint8")
    fields = proto.add_bit_fields()
    assert fields

    proto.add_field("test2", "uint8", enum="int1")
