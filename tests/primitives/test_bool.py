"""
Test the 'primitives.bool' module.
"""

# module under test
from runtimepy.primitives.bool import Bool


def test_bool_basic():
    """Test basic interactions with boolean primitives."""

    prim = Bool()
    prim.set()

    copied = prim.copy()
    assert copied()

    prim.clear()
    assert copied()
