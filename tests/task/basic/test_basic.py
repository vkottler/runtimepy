"""
Test the 'task.basic' module.
"""

# built-in
import asyncio

# third-party
from pytest import mark

# internal
from tests.resources import OverrunTask, SampleTask

BASE_PERIOD = 0.05


@mark.asyncio
async def test_periodic_task_overrun():
    """Test that the overrun counter increments properly."""

    task = OverrunTask("overrun")
    await task.task(period_s=BASE_PERIOD)

    # Allow it to run.
    assert await task.wait_iterations(BASE_PERIOD * 10)

    await task.stop()
    assert await task.wait_for_disable(0)
    assert task.metrics.overruns.value > 0


@mark.asyncio
async def test_periodic_task_basic():
    """Test basic interactions with periodic tasks."""

    base_period = BASE_PERIOD

    task = SampleTask("sample")

    # Create the initial task.
    initial = await task.task(base_period)

    # Allow it to run.
    assert await task.wait_iterations(base_period * 10, count=2)

    # Create a new instance of the task, causing the first one to be cancelled.
    new_task = await task.task(base_period * 2)

    # Ensure that the initial task completed on its own.
    assert initial.done()

    # Ensure the new task gets to run.
    await task.wait_iterations(base_period * 2)

    # Cancel the new task and ensure it stops.
    new_task.cancel()
    try:
        await new_task
        assert new_task.done()

    # This happens on Windows...
    except asyncio.CancelledError:
        pass


@mark.asyncio
async def test_periodic_task_stop_sig():
    """Test that periodic tasks stop when the stop signal is set."""

    task = SampleTask("sample")

    stop_sig = asyncio.Event()

    # Create the initial task.
    initial = await task.task(0.01, stop_sig=stop_sig)

    stop_sig.set()

    await initial
    assert initial.done()
