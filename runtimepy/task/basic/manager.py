"""
A module implementing a periodic-task manager.
"""

# built-in
import asyncio as _asyncio
from contextlib import asynccontextmanager as _asynccontextmanager
from typing import AsyncIterator as _AsyncIterator
from typing import Dict as _Dict

# internal
from runtimepy.task.basic.periodic import PeriodicTask as _PeriodicTask


class PeriodicTaskManager:
    """A class for managing periodic tasks as a single group."""

    def __init__(self) -> None:
        """Initialize this instance."""
        self._tasks: _Dict[str, _PeriodicTask] = {}

    def register(self, task: _PeriodicTask, period_s: float = None) -> bool:
        """Register a periodic task."""

        result = task.name not in self._tasks
        if result:
            self._tasks[task.name] = task
            task.set_period(period_s=period_s)
        return result

    def __getitem__(self, name: str) -> _PeriodicTask:
        """Get a task by name."""
        return self._tasks[name]

    async def start(self, stop_sig: _asyncio.Event = None) -> None:
        """Ensure tasks are started."""
        await _asyncio.gather(
            *(x.task(stop_sig=stop_sig) for x in self._tasks.values())
        )

    async def stop(self) -> None:
        """Ensure tasks are stopped."""
        await _asyncio.gather(*(x.stop() for x in self._tasks.values()))

    @_asynccontextmanager
    async def running(
        self, stop_sig: _asyncio.Event = None
    ) -> _AsyncIterator[None]:
        """Run tasks as an async context."""

        await self.start(stop_sig=stop_sig)
        try:
            yield
        finally:
            await self.stop()
