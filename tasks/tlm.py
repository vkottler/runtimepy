"""
A module implementing a simple telemetry sample interface.
"""

# built-in
import asyncio

# internal
from runtimepy.net.arbiter import AppInfo


async def sample_app(app: AppInfo) -> int:
    """Test telemetry sending and receiving."""

    iteration = 0
    forever = app.config_param("forever", False)
    while not app.stop.is_set() and (iteration < 31 or forever):
        iteration += 1
        await asyncio.sleep(0.01)

    return 0
