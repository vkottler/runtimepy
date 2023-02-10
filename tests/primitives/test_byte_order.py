"""
Test the 'primitives.byte_order' module.
"""

# module under test
from runtimepy.primitives.byte_order import ByteOrder


def test_byte_order_basic():
    """Test basic interactions with the byte-order enumeration."""

    for item in ByteOrder:
        assert str(item)
