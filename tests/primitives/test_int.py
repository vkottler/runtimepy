"""
Test the 'primitives.int' module.
"""

# built-in
import asyncio

# third-party
from pytest import mark

# module under test
from runtimepy.primitives.int import Int8


@mark.asyncio
async def test_int_evaluations():
    """Test the 'evaluate' interface using a boolean primitive."""

    prim = Int8()

    async def toggler() -> None:
        """Toggle a primitive after yielding."""
        await asyncio.sleep(0)
        prim.increment()

    task = asyncio.create_task(toggler())
    assert await prim.wait_for_value(prim.value + 1, 0.1)
    await task

    assert not await prim.wait_for_value(prim.value + 1, 0.0)
    assert await prim.wait_for_value(prim.value, 0.0)
