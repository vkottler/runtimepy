"""
Test the 'task.async' module.
"""

# built-in
import asyncio
from unittest.mock import patch

# module under test
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.task import AsyncTask


class SampleTask(AsyncTask):
    """A sample task implementation."""

    async def dispatch(self) -> bool:
        """Dispatch this task."""

        # Only run dispatch five times.
        if self.dispatches.raw.value >= 20:
            return False

        return await super().dispatch()


def test_async_task_basic():
    """Test that a basic task can run."""

    task = SampleTask("test", 0.01, ChannelEnvironment())
    asyncio.run(task.run())

    # Cause sleep to raise a cancelled error.
    with patch("runtimepy.task._asyncio.sleep") as mocked:
        mocked.side_effect = asyncio.CancelledError
        asyncio.run(task.run())
