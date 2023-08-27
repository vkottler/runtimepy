"""
Test the 'primitives.array' module.
"""

# built-in
from io import BytesIO
from typing import cast

# module under test
from runtimepy.primitives import create
from runtimepy.primitives.array import PrimitiveArray
from runtimepy.primitives.bool import Bool
from runtimepy.primitives.float import Double, Float
from runtimepy.primitives.int import Int32


def test_primitive_array_basic():
    """Test basic usages of primitive arrays."""

    bool1: Bool = cast(Bool, create("bool"))
    bool2: Bool = cast(Bool, create("bool"))

    def bool_changed(curr: bool, new: bool) -> None:
        """A sample value-change callback."""
        assert curr != new

    bool1.register_callback(bool_changed, once=True)

    int1: Int32 = cast(Int32, create("int32"))
    int2: Int32 = cast(Int32, create("int32"))

    float1: Float = cast(Float, create("float"))
    float2: Double = cast(Double, create("double"))

    array = PrimitiveArray(bool1, bool2, int1, int2, float1, float2)

    # Set some values.
    array[0](True)
    int1(-1)
    int2(-2)
    float1(-1.0)
    float2(2.0)

    # Write values to a stream.
    with BytesIO() as stream:
        assert array.to_stream(stream) == 22
        to_update = stream.getvalue()

    # Set different values.
    array[0](False)
    array[1](True)
    int1(1)
    int2(2)
    float1(1.0)
    float2(2.0)

    with BytesIO() as stream:
        stream.write(to_update)
        stream.seek(0)
        array.from_stream(stream)

    assert array[0]() is True
    assert array[1]() is False
    assert int1 == -1
    assert int2 == -2
    assert float1 == -1.0
    assert float2 == 2.0

    copied = array.copy()
    assert copied[0]() is True
    assert copied[1]() is False


def sample_array() -> PrimitiveArray:
    """Create a new, sample array for testing."""

    return PrimitiveArray(
        create("bool"),  # 0
        create("bool"),  # 1
        create("int16"),  # 2
        create("int16"),  # 3
        create("int32"),  # 4
        create("int32"),  # 5
        create("int64"),  # 6
        create("int64"),  # 7
        create("float"),  # 8
        create("double"),  # 9
    )


def test_primitive_array_fragmenting_through_end():
    """
    Test that way can create array fragments that include the last element(s).
    """

    array = sample_array()

    idx = array.fragment_from_indices(1)
    assert array.fragment(idx).size == 41

    idx = array.fragment_from_indices(1, 10)
    assert array.fragment(idx).size == 41

    idx = array.fragment_from_byte_indices(1)
    assert array.fragment(idx).size == 41

    idx = array.fragment_from_byte_indices(1, 42)
    assert array.fragment(idx).size == 41


def test_primitive_array_fragmenting_basic():
    """Test interactions with array fragments."""

    array = sample_array()
    assert array.num_fragments == 0

    idx = array.fragment_from_indices(0, 1)
    assert array.num_fragments == 1

    assert array.fragment(idx).size == 1

    copied = array.copy()
    assert copied.fragment(idx).size == 1

    # Set the underlying value to true.
    array[0](True)

    assert copied[0].value is False

    copied.update_fragment(idx, array.fragment_bytes(idx))

    assert copied[0].value is True


def test_primitive_array_indexing():
    """Test the correctness of various index lookup functions."""

    array = sample_array()

    for _ in range(3):
        assert array.size == 42

        # Check index->bytes.
        assert array.byte_at_index(0) == 0
        assert array.byte_at_index(1) == 1
        assert array.byte_at_index(2) == 2
        assert array.byte_at_index(3) == 4
        assert array.byte_at_index(4) == 6
        assert array.byte_at_index(5) == 10
        assert array.byte_at_index(6) == 14
        assert array.byte_at_index(7) == 22
        assert array.byte_at_index(8) == 30
        assert array.byte_at_index(9) == 34
        assert array.byte_at_index(10) == array.size

        # Check bytes->index.
        assert array.index_at_byte(0) == 0
        assert array.index_at_byte(1) == 1
        assert array.index_at_byte(2) == 2
        assert array.index_at_byte(4) == 3
        assert array.index_at_byte(6) == 4
        assert array.index_at_byte(10) == 5
        assert array.index_at_byte(14) == 6
        assert array.index_at_byte(22) == 7
        assert array.index_at_byte(30) == 8
        assert array.index_at_byte(34) == 9
        assert array.index_at_byte(array.size) == 10

        array.reset()
        for item in [
            "bool",
            "bool",
            "int16",
            "int16",
            "int32",
            "int32",
            "int64",
            "int64",
            "float",
            "double",
        ]:
            array.add(create(item))
