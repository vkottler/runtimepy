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
    assert prim == "test"
    assert prim.size == 6

    assert hash(prim)

    with BytesIO() as stream:
        assert prim.write(stream) == 6
        stream.seek(0)

        assert prim.read(stream) == "test"

        stream.seek(0)
        prim.set("Hello, world!")
        assert prim.write(stream) == 15
        stream.seek(0)

        new_prim = StringPrimitive.from_stream(stream)
        assert new_prim == "Hello, world!" == str(new_prim)

    assert StringPrimitive("test_test").size == 11
