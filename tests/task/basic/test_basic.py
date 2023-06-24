"""
Test the 'task.basic' module.
"""

# built-in
import asyncio

# third-party
from pytest import mark

# module under test
from runtimepy.task.basic import PeriodicTask


class SampleTask(PeriodicTask):
    """A sample task."""

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

        self.logger.info("Iteration.")
        return True


@mark.asyncio
async def test_periodic_task_basic():
    """Test basic interactions with periodic tasks."""

    base_period = 0.05

    task = SampleTask("sample")

    # Create the initial task.
    initial = await task.task(base_period)

    # Allow it to run.
    await asyncio.sleep(base_period * 2)

    # Create a new instance of the task, causing the first one to be cancelled.
    new_task = await task.task(base_period * 2)

    # Ensure that the initial task completed on its own.
    assert initial.done()

    # Ensure the new task gets to run.
    await asyncio.sleep(base_period * 2)

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
