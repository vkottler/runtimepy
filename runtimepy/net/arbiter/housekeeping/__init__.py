"""
A module implementing various housekeeping tasks for the connection-arbiter
runtime.
"""

# internal
from runtimepy.net.arbiter.info import AppInfo as _AppInfo
from runtimepy.net.arbiter.task import ArbiterTask as _ArbiterTask
from runtimepy.net.arbiter.task import TaskFactory as _TaskFactory
from runtimepy.net.manager import ConnectionManager as _ConnectionManager


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

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

        self.manager.poll_metrics()
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


def metrics_poller(
    manager: _ConnectionManager, period_s: float = 0.5
) -> ConnectionMetricsPoller:
    """Create a metrics-polling task."""

    return ConnectionMetricsPoller(
        "connection_metrics_poller", manager, period_s=period_s
    )
