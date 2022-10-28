"""
Test the 'primitives.type' module.
"""

# module under test
from runtimepy.primitives.type import normalize


def test_primitive_type_basic():
    """Test basic interactions with the primitive type system."""

    assert normalize("uint8") != normalize("int8")
    assert hash(normalize("uint8"))
