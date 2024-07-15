"""
Test the 'primitives.int' module.
"""

# built-in
import asyncio

# third-party
from pytest import mark

# module under test
from runtimepy.primitives.evaluation import sample_for
from runtimepy.primitives.int import Int8


@mark.asyncio
async def test_int_evaluations_scaling():
    """
    Test the 'evaluate' interface using an integer primitive with a scaling
    polynomial.
    """

    prim = Int8(value=1, scaling=[1.0, 2.0])
    assert prim.scaled == 3

    # Should succeed immediately.
    assert await prim.wait_for_value(3, 0.0)
    assert await prim.wait_for_value(3.0, 0.0)
    assert await prim.wait_for_value(3.1, 0.0)

    async def incrementer() -> None:
        """Increment a primitive after yielding."""
        await asyncio.sleep(0)
        prim.increment()

    task = asyncio.create_task(incrementer())
    assert await prim.wait_for_value(5, 0.1)
    assert await prim.wait_for_value(5.0, 0.1)
    assert await prim.wait_for_value(5.1, 0.1)
    await task

    # Expect only one value.
    curr = (prim.value, prim.last_updated_ns)

    samples = []
    async for sample in sample_for(prim, 0.0, count=1):
        samples.append(sample)
    assert len(samples) == 1
    assert samples[0] == curr

    # Time out.
    samples = []
    async for sample in sample_for(prim, 0.0, count=2):
        samples.append(sample)
    assert len(samples) == 1
    assert samples[0] == curr

    # Actual sampling.
    for idx in range(10):
        samples = []
        async for sample in sample_for(prim, 0.0, count=idx + 2):
            samples.append(sample)
            prim.increment()
        assert len(samples) == idx + 2


@mark.asyncio
async def test_int_evaluations():
    """Test the 'evaluate' interface using an integer primitive."""

    prim = Int8()

    async def incrementer() -> None:
        """Toggle a primitive after yielding."""
        await asyncio.sleep(0)
        prim.increment()

    task = asyncio.create_task(incrementer())
    assert await prim.wait_for_value(prim.value + 1, 0.1)
    await task

    assert not await prim.wait_for_value(prim.value + 1, 0.0)
    assert await prim.wait_for_value(prim.value, 0.0)
