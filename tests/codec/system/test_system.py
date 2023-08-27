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

    system.enum("TestEnum1", {"a": 1, "b": 2, "c": 3})

    new_type.add_field("a", enum="TestEnum1")
    assert new_type.array.size == 1

    system.enum("TestEnum2", {"a": 1, "b": 2, "c": 3}, primitive="uint16")
    new_type.add_field("b", enum="TestEnum2")
    assert new_type.array.size == 3
    assert system.size("SomeStruct") == 3
