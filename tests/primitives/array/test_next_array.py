"""
Test the 'primitives.array' module.
"""

# module under test
from runtimepy.primitives.array import PrimitiveArray


def test_primitive_array_next():
    """Test basic array-chaining scenarios."""

    head = PrimitiveArray()
    assert head

    # need a method to be able to add by string type name
    # head.add()
