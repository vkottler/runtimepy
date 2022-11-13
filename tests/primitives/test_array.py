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
