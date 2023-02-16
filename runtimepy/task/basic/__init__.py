"""
A module implementing a simple periodic-task interface.
"""

from __future__ import annotations

# built-in
from abc import ABC as _ABC
from abc import abstractmethod as _abstractmethod
import asyncio as _asyncio
from contextlib import suppress
from logging import getLogger as _getLogger
from typing import Optional as _Optional

# third-party
from vcorelib.logging import LoggerMixin as _LoggerMixin

# internal
from runtimepy.task import rate_str as _rate_str


class PeriodicTask(_LoggerMixin, _ABC):
    """A class implementing a simple periodic-task interface."""

    def __init__(self, name: str) -> None:
        """Initialize this task."""

        self.name = name
        super().__init__(logger=_getLogger(self.name))
        self.enabled = False
        self._task: _Optional[_asyncio.Task[None]] = None

    @_abstractmethod
    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

    async def _run(self, period_s: float) -> None:
        """
        Run this task by executing the dispatch method at the specified period
        until a dispatch iteration fails or the task is otherwise disabled.
        """

        assert not self.enabled
        self.enabled = True

        self.logger.info("Task starting at %s.", _rate_str(period_s))

        eloop = _asyncio.get_running_loop()

        while self.enabled:
            start = eloop.time()
            self.enabled = await _asyncio.shield(self.dispatch())
            iter_time = eloop.time() - start

            if self.enabled:
                try:
                    await _asyncio.sleep(max(period_s - iter_time, 0))
                except _asyncio.CancelledError:
                    self.logger.info("Task was cancelled.")
                    self.enabled = False

        self.logger.info("Task completed.")

    async def task(self, period_s: float) -> _asyncio.Task[None]:
        """Create an event-loop task for this periodic."""

        # Ensure that a previous version of this task gets cleaned up.
        if self._task is not None:
            if not self._task.done():
                # On Windows, setting enabled False here is not enough.
                self.enabled = False
                self._task.cancel()
                with suppress(_asyncio.CancelledError):
                    await self._task
            self._task = None

        self._task = _asyncio.create_task(self._run(period_s))
        return self._task
