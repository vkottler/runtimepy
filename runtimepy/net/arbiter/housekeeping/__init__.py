"""
A module implementing various housekeeping tasks for the connection-arbiter
runtime.
"""

# built-in
import asyncio

# internal
from runtimepy.mixins.async_command import AsyncCommandProcessingMixin
from runtimepy.net.arbiter.info import AppInfo as _AppInfo
from runtimepy.net.arbiter.task import ArbiterTask as _ArbiterTask
from runtimepy.net.arbiter.task import TaskFactory as _TaskFactory
from runtimepy.net.manager import ConnectionManager as _ConnectionManager
from runtimepy.primitives import Bool


class ConnectionMetricsPoller(_ArbiterTask):
    """A class that periodically polls connection metrics."""

    def __init__(
        self,
        name: str,
        manager: _ConnectionManager,
        **kwargs,
    ) -> None:
        """Initialize this task."""

        super().__init__(name, **kwargs)
        self.manager = manager

    def _init_state(self) -> None:
        """Add channels to this instance's channel environment."""

        # Channel control for polling connection metrics.
        self.poll_connection_metrics = Bool()
        self.env.channel(
            "poll_connection_metrics",
            self.poll_connection_metrics,
            commandable=True,
            description="Polls application connection metrics when true.",
        )

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

        if self.poll_connection_metrics:
            self.manager.poll_metrics()

        # Handle any incoming commands.
        processors = []
        for mapping in self.app.connections.values(), self.app.tasks.values():
            for item in mapping:
                if isinstance(item, AsyncCommandProcessingMixin):
                    processors.append(item.process_command_queue())

        if processors:
            await asyncio.gather(*processors)

        return True


class ConnectionMetricsLogger(_ArbiterTask):
    """A task for logging metrics."""

    app: _AppInfo

    def _log(self) -> None:
        """Log metrics to console."""
        for name, conn in self.app.connections.items():
            conn.log_metrics(label=name)

    async def init(self, app: _AppInfo) -> None:
        """Initialize this task with application information."""
        self.app = app
        self._log()

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""
        self._log()
        return True


class ConnectionMetricsLoggerFactory(_TaskFactory[ConnectionMetricsLogger]):
    """A factory for the connection-metrics logger."""

    kind = ConnectionMetricsLogger


def housekeeping(
    manager: _ConnectionManager,
    period_s: float = 0.1,
    poll_connection_metrics: bool = True,
) -> ConnectionMetricsPoller:
    """Create a metrics-polling task."""

    task = ConnectionMetricsPoller("housekeeping", manager, period_s=period_s)
    task.poll_connection_metrics.value = poll_connection_metrics
    return task
