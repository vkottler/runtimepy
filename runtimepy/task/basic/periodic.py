"""
A module implementing a basic periodic task.
"""

from __future__ import annotations

# built-in
from abc import ABC as _ABC
from abc import abstractmethod as _abstractmethod
import asyncio as _asyncio
from contextlib import suppress as _suppress
from logging import getLogger as _getLogger
from typing import Optional as _Optional

# third-party
from vcorelib.logging import LoggerMixin as _LoggerMixin
from vcorelib.math import DEFAULT_DEPTH as _DEFAULT_DEPTH
from vcorelib.math import MovingAverage as _MovingAverage
from vcorelib.math import RateTracker as _RateTracker
from vcorelib.math import rate_str as _rate_str

# internal
from runtimepy.primitives import Bool as _Bool
from runtimepy.task.basic.metrics import PeriodicTaskMetrics


class PeriodicTask(_LoggerMixin, _ABC):
    """A class implementing a simple periodic-task interface."""

    def __init__(
        self,
        name: str,
        average_depth: int = _DEFAULT_DEPTH,
        metrics: PeriodicTaskMetrics = None,
        period_s: float = None,
    ) -> None:
        """Initialize this task."""

        self.name = name
        super().__init__(logger=_getLogger(self.name))
        self._task: _Optional[_asyncio.Task[None]] = None

        self._period_s: _Optional[float] = None
        self.set_period(period_s=period_s)

        # Setup runtime state.
        self._enabled = _Bool()

        if metrics is None:
            metrics = PeriodicTaskMetrics.create()
        self.metrics = metrics

        self._dispatch_rate = _RateTracker(depth=average_depth)
        self._dispatch_time = _MovingAverage(depth=average_depth)

    def set_period(self, period_s: float = None) -> bool:
        """Attempt to set a new period for this task."""

        result = False

        if period_s is not None and self._period_s != period_s:
            self._period_s = period_s
            self.logger.info("Task rate set to %s.", _rate_str(period_s))
            result = True

        return result

    @_abstractmethod
    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

    def disable(self) -> bool:
        """Disable this task, return whether or not any action was taken."""

        result = bool(self._enabled)
        if result:
            self._enabled.clear()
        return result

    async def run(
        self, period_s: float = None, stop_sig: _asyncio.Event = None
    ) -> None:
        """
        Run this task by executing the dispatch method at the specified period
        until a dispatch iteration fails or the task is otherwise disabled.
        """

        assert not self._enabled
        self._enabled.raw.value = True

        self.set_period(period_s=period_s)
        assert self._period_s is not None, "Task period isn't set!"
        self.logger.info("Task starting at %s.", _rate_str(self._period_s))

        eloop = _asyncio.get_running_loop()

        while self._enabled:
            start = eloop.time()

            # Keep track of the rate that this task is running at.
            self.metrics.rate_hz.raw.value = self._dispatch_rate(
                int(start * 1e9)
            )

            self._enabled.raw.value = await _asyncio.shield(self.dispatch())
            iter_time = eloop.time() - start

            # Update runtime metrics.
            self.metrics.dispatches.raw.value += 1
            self.metrics.average_s.raw.value = self._dispatch_time(iter_time)
            self.metrics.max_s.raw.value = self._dispatch_time.max
            self.metrics.min_s.raw.value = self._dispatch_time.min

            # Check this synchronously. This may not be suitable for tasks
            # with long periods.
            if stop_sig is not None:
                self._enabled.raw.value = not stop_sig.is_set()

            sleep_s = self._period_s - iter_time

            if self._enabled:
                try:
                    await _asyncio.sleep(max(sleep_s, 0))
                except _asyncio.CancelledError:
                    self.logger.info("Task was cancelled.")
                    self.disable()

        self.logger.info("Task completed.")

    async def stop(self) -> bool:
        """Wait for this task to stop running (if it is)."""

        result = False

        # Ensure that a previous version of this task gets cleaned up.
        if self._task is not None:
            if not self._task.done():
                # On Windows, setting enabled False here is not enough.
                self.disable()
                self._task.cancel()
                with _suppress(_asyncio.CancelledError):
                    await self._task
            self._task = None
            result = True

        return result

    async def task(
        self, period_s: float = None, stop_sig: _asyncio.Event = None
    ) -> _asyncio.Task[None]:
        """Create an event-loop task for this periodic."""

        await self.stop()
        self._task = _asyncio.create_task(
            self.run(period_s=period_s, stop_sig=stop_sig)
        )
        return self._task
