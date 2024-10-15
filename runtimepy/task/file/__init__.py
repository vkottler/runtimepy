"""
A module implementing file-related task interfaces.
"""

# built-in
import os
from pathlib import Path

# internal
from runtimepy.mixins.logging import LogCaptureMixin
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.arbiter.task import ArbiterTask as _ArbiterTask
from runtimepy.net.arbiter.task import TaskFactory as _TaskFactory


class LogCaptureTask(_ArbiterTask, LogCaptureMixin):
    """
    A task that captures all log messages emitted by this program instance.
    """

    auto_finalize = True

    async def init(self, app: AppInfo) -> None:
        """Initialize this task with application information."""

        await super().init(app)

        # See above comment, we can probably keep the mixin class but delete
        # this one - unless we want a separate "Linux" task to run / handle
        # this (we might want to increase the housekeeping task rate to reduce
        # async command latency + connection processing?).
        await self.init_log_capture(
            app.stack, [("info", Path(os.sep, "var", "log", "syslog"))]
        )

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

        await self.dispatch_log_capture()
        return True


class LogCapture(_TaskFactory[LogCaptureTask]):
    """A factory for the syslog capture task."""

    kind = LogCaptureTask
