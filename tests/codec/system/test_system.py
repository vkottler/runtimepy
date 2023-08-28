"""
Ttest the 'codec.system' module.
"""

# module under test
from runtimepy.codec.system import TypeSystem


def get_test_system() -> TypeSystem:
    """Get a simple test system."""

    system = TypeSystem("test")

    system.enum("TestEnum1", {"a": 1, "b": 2, "c": 3})
    system.enum("TestEnum2", {"a": 1, "b": 2, "c": 3}, primitive="uint16")

    system.register("SampleStruct")
    system.add("SampleStruct", "enum1", "TestEnum1")
    system.add("SampleStruct", "enum2", "TestEnum2")
    system.add("SampleStruct", "field", "uint32")

    assert system.size("SampleStruct") == 7

    return system


def test_type_system_compound_types():
    """Test a custom type system with multiple complex types."""

    system = get_test_system()

    system.register("SomeStruct")
    assert system.size("SomeStruct") == 0

    system.add("SomeStruct", "enum1", "TestEnum1")
    system.add("SomeStruct", "enum2", "TestEnum2")
    system.add("SomeStruct", "field", "uint32")

    system.add("SomeStruct", "sample", "SampleStruct")

    system.add("SomeStruct", "field2", "int16")

    assert system.size("SomeStruct") == 16


def test_type_system_basic():
    """Test basic interactions with a custom type system."""

    system = get_test_system()

    assert system.size("runtimepy::ByteOrder") == 1

    new_type = system.register("SomeStruct")
    assert system.size("SomeStruct") == 0

    system.add("SomeStruct", "a", "TestEnum1")
    assert new_type.array.size == 1

    system.add("SomeStruct", "b", "TestEnum2")
    assert new_type.array.size == 3

    assert system.size("SomeStruct") == 3

    for field in [
        "uint8",
        "uint16",
        "uint32",
        "uint64",
        "int8",
        "int16",
        "int32",
        "int64",
        "float",
        "double",
    ]:
        system.add("SomeStruct", f"{field}_field", field)
