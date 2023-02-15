"""
Test the 'primitives.string' module.
"""

# built-in
from io import BytesIO

# module under test
from runtimepy.primitives.string import StringPrimitive


def test_string_primitive_basic():
    """Test basic interactions with string primitives."""

    prim = StringPrimitive()
    prim.set("test")
    assert prim.value == "test"
    assert prim.size == 6

    with BytesIO() as stream:
        prim.write(stream)
        stream.seek(0)
        assert prim.read(stream) == "test"
