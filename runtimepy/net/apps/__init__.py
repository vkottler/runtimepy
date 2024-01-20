"""
A module aggregating commonly used network applications (that use the
connection-arbiter technology).
"""

# internal
from runtimepy.net.arbiter import AppInfo, init_only

__all__ = [
    "AppInfo",
    "init_only",
    "wait_for_stop",
    "noop",
    "fail",
    "exception",
]


async def wait_for_stop(app: AppInfo) -> int:
    """Waits for the stop signal to be set."""

    result = await init_only(app)
    await app.stop.wait()
    return result


noop = init_only


async def fail(app: AppInfo) -> int:
    """Waits for the stop signal to be set."""

    del app
    return 1


async def exception(app: AppInfo) -> int:
    """Waits for the stop signal to be set."""

    del app
    assert False
