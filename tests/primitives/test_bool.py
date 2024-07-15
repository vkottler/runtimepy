"""
Test the 'primitives.bool' module.
"""

# built-in
import asyncio

# third-party
from pytest import mark

# module under test
from runtimepy.primitives.bool import Bool


@mark.asyncio
async def test_bool_evaluations():
    """Test the 'evaluate' interface using a boolean primitive."""

    prim = Bool()

    async def toggler() -> None:
        """Toggle a primitive after yielding."""
        await asyncio.sleep(0)
        prim.toggle()

    task = asyncio.create_task(toggler())
    assert await prim.wait_for_state(not bool(prim), 0.1)
    await task

    assert not await prim.wait_for_state(not bool(prim), 0.0)
    assert await prim.wait_for_state(bool(prim), 0.0)


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
