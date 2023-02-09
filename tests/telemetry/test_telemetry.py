"""
Test the 'telemetry' module.
"""

# module under test
from runtimepy.enum.registry import EnumRegistry
from runtimepy.telemetry import MessageType


def test_message_type_basic():
    """Test basic interactions with the message-type enumeration."""

    enum = MessageType.runtime_enum(1)
    assert enum.get_int("protocol_meta") == 1
    assert enum.get_int("protocol_data") == 2

    enum_reg = EnumRegistry({})
    enum = MessageType.register_enum("protocol", enum_reg)
    assert enum.get_int("protocol_meta") == 1
    assert enum.get_int("protocol_data") == 2
