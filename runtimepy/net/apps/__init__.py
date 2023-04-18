"""
A module aggregating commonly used network applications (that use the
connection-arbiter technology).
"""

# internal
from runtimepy.net.arbiter import AppInfo, init_only

__all__ = ["AppInfo", "init_only", "wait_for_stop"]


async def wait_for_stop(app: AppInfo) -> int:
    """Waits for the stop signal to be set."""

    await app.stop.wait()
    return 0
