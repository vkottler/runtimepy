"""
Test the 'primitives.field.fields' module.
"""

# third-party
from pytest import raises

# module under test
from runtimepy.primitives.field.fields import BitFields

# internal
from tests.resources import resource


def test_bit_fields_basic():
    """Test basic interactions with a bit-fields."""

    byte = BitFields.new()

    flag1 = byte.flag("flag1")
    assert flag1.where_str() == "^-------"

    flag2 = byte.flag("flag2")
    assert flag2.where_str() == "-^------"

    flag1.set()
    assert byte.raw.value == 1

    flag2.set()
    assert byte.raw.value == 3

    flag1.clear()
    assert byte.raw.value == 2

    assert flag2.get() is True
    assert flag1.get() is False

    field1 = byte.field("field1", 2)
    assert field1(val=7) == 3

    assert byte.raw.value == 14


def test_bit_fields_load():
    """Test loading bit-fields from a configuration file."""

    word = BitFields.decode(resource("fields", "sample_fields.yaml"))

    # Set some values.
    assert word[4]() == 1

    assert word.raw == 17

    # Verify the underlying value.
    assert word.flag("new_flag").index == 13

    with raises(KeyError):
        assert word[30]

    assert word.get_field("field0")

    word.finalize()
