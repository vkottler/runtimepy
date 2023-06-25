"""
Test the 'runtimepy.task.basic.manager' module.
"""

# built-in
import asyncio

# third-party
from pytest import mark

# module under test
from runtimepy.task import PeriodicTaskManager

# internal
from tests.resources import SampleTask


@mark.asyncio
async def test_periodic_task_manager_basic():
    """Test basic interactions with a periodic-task manager."""

    manager = PeriodicTaskManager()

    base_period = 0.05

    task = SampleTask("sample")
    assert manager.register(task, period_s=base_period)
    assert manager["sample"] is task

    async with manager.running():
        await asyncio.sleep(base_period * 2)
