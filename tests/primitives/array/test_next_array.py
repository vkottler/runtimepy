"""
Test the 'primitives.array' module.
"""

# module under test
from runtimepy.primitives.array import PrimitiveArray
from runtimepy.primitives.serializable.prefixed import PrefixedChunk


def test_primitive_array_next():
    """Test basic array-chaining scenarios."""

    head = PrimitiveArray()

    head.add_primitive("uint8")
    head.add_primitive("uint8")
    head.add_primitive("uint16")
    head.add_primitive("uint16")

    head.assign(PrimitiveArray())

    head.add_primitive("uint8")
    head.add_primitive("uint8")
    head.add_primitive("uint16")
    head.add_primitive("uint16")

    assert head.size == 6

    head.add_to_end(PrefixedChunk.create())
    head.add_to_end(PrefixedChunk.create())

    head.add_primitive("uint8")
    head.add_primitive("uint8")
    head.add_primitive("uint16")
    head.add_primitive("uint16")
