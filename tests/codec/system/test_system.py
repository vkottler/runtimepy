"""
Ttest the 'codec.system' module.
"""

# module under test
from runtimepy.codec.system import TypeSystem


def test_type_system_basic():
    """Test basic interactions with a custom type system."""

    system = TypeSystem("test")

    assert system.size("ByteOrder") == 1

    new_type = system.register("SomeStruct")
    assert new_type

    assert system.size("SomeStruct") == 0
