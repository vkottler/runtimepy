"""
Test the 'primitives.field.manager' module.
"""

# module under test
from runtimepy.primitives.field.manager import BitFieldManager


def test_bit_field_manager_basic():
    """Test basic interactions with a bit-field manager."""

    byte = BitFieldManager.create()

    flag1 = byte.flag()
    flag2 = byte.flag()

    flag1.set()
    assert byte.raw.value == 1

    flag2.set()
    assert byte.raw.value == 3

    flag1.clear()
    assert byte.raw.value == 2

    assert flag2.get() is True
    assert flag1.get() is False

    field1 = byte.field(2)
    assert field1(val=7) == 3

    assert byte.raw.value == 14
