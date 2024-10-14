"""
A module implementing file-related task interfaces.
"""

# third-party
from vcorelib.paths import Pathlike

# internal
from runtimepy.mixins.logging import SYSLOG, LogCaptureMixin
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.arbiter.task import ArbiterTask as _ArbiterTask
from runtimepy.net.arbiter.task import TaskFactory as _TaskFactory


class LogCaptureTask(_ArbiterTask, LogCaptureMixin):
    """
    A task that captures all log messages emitted by this program instance.
    """

    auto_finalize = True

    log_paths: list[Pathlike] = [SYSLOG]

    async def init(self, app: AppInfo) -> None:
        """Initialize this task with application information."""

        await super().init(app)

        # Allow additional paths via configuration?
        await self.init_log_capture(app.stack, self.log_paths)

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

        await self.dispatch_log_capture()
        return True


class LogCapture(_TaskFactory[LogCaptureTask]):
    """A factory for the syslog capture task."""

    kind = LogCaptureTask
