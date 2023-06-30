"""
A module implementing various housekeeping tasks for the connection-arbiter
runtime.
"""

# internal
from runtimepy.net.arbiter.task import ArbiterTask as _ArbiterTask
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


def metrics_poller(
    manager: _ConnectionManager, period_s: float = 0.5
) -> ConnectionMetricsPoller:
    """Create a metrics-polling task."""

    return ConnectionMetricsPoller(
        "connection_metrics_poller", manager, period_s=period_s
    )
