"""
A module implementing a periodic-task manager.
"""

# built-in
import asyncio as _asyncio
from contextlib import asynccontextmanager as _asynccontextmanager
from typing import AsyncIterator as _AsyncIterator
from typing import Generic as _Generic
from typing import Iterator as _Iterator
from typing import TypeVar as _TypeVar

# internal
from runtimepy.task.basic.periodic import PeriodicTask as _PeriodicTask

T = _TypeVar("T", bound=_PeriodicTask)


class PeriodicTaskManager(_Generic[T]):
    """A class for managing periodic tasks as a single group."""

    def __init__(self) -> None:
        """Initialize this instance."""
        self._tasks: dict[str, T] = {}

    def register(self, task: T, period_s: float = None) -> bool:
        """Register a periodic task."""

        result = task.name not in self._tasks
        if result:
            self._tasks[task.name] = task
            task.set_period(period_s=period_s)
        return result

    @property
    def tasks(self) -> _Iterator[T]:
        """Iterate over tasks."""
        yield from self._tasks.values()

    def __getitem__(self, name: str) -> T:
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
