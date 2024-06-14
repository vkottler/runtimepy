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

    call_count = 0

    def change_cb(_: bool, __: bool) -> None:
        """A sample callback."""
        nonlocal call_count
        call_count += 1

    with prim.callback(change_cb):
        prim.toggle()
        prim.toggle()

    prim.toggle()
    prim.toggle()

    assert call_count == 2
