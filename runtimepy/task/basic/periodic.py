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
from vcorelib.io.markdown import MarkdownMixin
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.math import DEFAULT_DEPTH as _DEFAULT_DEPTH
from vcorelib.math import MovingAverage as _MovingAverage
from vcorelib.math import RateTracker as _RateTracker
from vcorelib.math import rate_str as _rate_str

# internal
from runtimepy import PKG_NAME
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
)
from runtimepy.metrics import PeriodicTaskMetrics
from runtimepy.mixins.environment import ChannelEnvironmentMixin
from runtimepy.mixins.logging import LoggerMixinLevelControl
from runtimepy.primitives import Bool as _Bool
from runtimepy.primitives import Double as _Double
from runtimepy.primitives import Float as _Float
from runtimepy.primitives.evaluation import EvalResult as _EvalResult
from runtimepy.ui.controls import Controlslike


class PeriodicTask(
    LoggerMixinLevelControl, ChannelEnvironmentMixin, MarkdownMixin, _ABC
):
    """A class implementing a simple periodic-task interface."""

    auto_finalize = True

    def __init__(
        self,
        name: str,
        average_depth: int = _DEFAULT_DEPTH,
        metrics: PeriodicTaskMetrics = None,
        period_s: float = 1.0,
        env: ChannelEnvironment = None,
        period_controls: Controlslike = "period",
        markdown: str = None,
        config: _JsonObject = None,
    ) -> None:
        """Initialize this task."""

        self.name = name

        self.set_markdown(markdown=markdown, config=config, package=PKG_NAME)
        self.config: _JsonObject = config or {}

        LoggerMixinLevelControl.__init__(self, logger=_getLogger(self.name))
        self._task: _Optional[_asyncio.Task[None]] = None

        # Setup runtime state.
        self._enabled = _Bool()

        if metrics is None:
            metrics = PeriodicTaskMetrics.create()
        self.metrics = metrics

        ChannelEnvironmentMixin.__init__(self, env=env)
        self.setup_level_channel(self.env)
        self.command = ChannelCommandProcessor(self.env, self.logger)
        self.register_task_metrics(self.metrics)

        # State.
        self.paused = _Bool()
        self.env.channel(
            "paused",
            self.paused,
            commandable=True,
            description="Whether or not this task is paused.",
        )

        self.period_s = _Float()
        self.env.channel(
            "period_s",
            self.period_s,
            commandable=True,
            description="Iteration period for this task.",
            controls=period_controls,
        )
        self.set_period(period_s=period_s)

        self._init_state()
        if self.auto_finalize:
            self.env.finalize()

        self._dispatch_rate = _RateTracker(depth=average_depth)
        self._dispatch_time = _MovingAverage(depth=average_depth)

    def _init_state(self) -> None:
        """Add channels to this instance's channel environment."""

    def set_period(
        self, period_s: float = None, update_default: bool = True
    ) -> bool:
        """Attempt to set a new period for this task."""

        result = False

        if period_s is not None and self.period_s != period_s:
            self.period_s.value = period_s

            if update_default:
                self.env.set_default("period_s", period_s)

            self.logger.debug(
                "Task rate set to %s.", _rate_str(self.period_s.value)
            )
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

    async def wait_for_disable(
        self, timeout: float, value: bool = False
    ) -> _EvalResult:
        """Wait for a task to become disabled."""
        return await self._enabled.wait_for_state(value, timeout)

    async def wait_iterations(self, timeout: float, count: int = 1) -> bool:
        """Wait for a task to complete a certain number of iterations."""

        return bool(
            await self.metrics.dispatches.wait_for_increment(
                timeout, count=count
            )
        )

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
        assert self.period_s is not None, "Task period isn't set!"
        self.logger.info(
            "Task starting at %s.", _rate_str(self.period_s.value)
        )

        iter_time = _Double()

        while self._enabled:
            # When paused, don't run the iteration itself.
            if not self.paused:
                with self.metrics.measure(
                    self._dispatch_rate,
                    self._dispatch_time,
                    iter_time,
                    self.period_s.value,
                ):
                    self._enabled.raw.value = await _asyncio.shield(
                        self.dispatch()
                    )

            # Check this synchronously. This may not be suitable for tasks
            # with long periods.
            if self._enabled and stop_sig is not None:
                self._enabled.raw.value = not stop_sig.is_set()

            if self._enabled:
                try:
                    sleep_time = max(self.period_s.value - iter_time.value, 0)

                    # Eventually run feedback control.

                    await _asyncio.sleep(sleep_time)
                except _asyncio.CancelledError:
                    self.logger.debug("Task was cancelled.")
                    self.disable()

        self.logger.debug("Task completed.")

    async def stop_extra(self) -> None:
        """Extra actions to perform when this task is stopping."""

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

            await self.stop_extra()
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
