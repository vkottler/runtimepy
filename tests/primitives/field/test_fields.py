"""
Test the 'primitives.field.fields' module.
"""

# module under test
from runtimepy.primitives.field.fields import BitFields

# internal
from tests.resources import resource


def test_bit_fields_basic():
    """Test basic interactions with a bit-fields."""

    byte = BitFields.new()

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


def test_bit_fields_load():
    """Test loading bit-fields from a configuration file."""

    word = BitFields.decode(resource("fields", "sample_fields.yaml"))

    # Set some values.
    assert word.flags[0].get()
    assert word.fields[4]() == 1

    assert word.raw == 17

    # Verify the underlying value.
    assert word.flag().index == 12
