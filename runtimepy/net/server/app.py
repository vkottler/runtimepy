"""
A module implementing application methods for this package's server interface.
"""

# internal
from runtimepy.net.arbiter.info import AppInfo


async def setup(app: AppInfo) -> int:
    """Perform server application setup steps."""

    print(app)

    # register handler for test websocket app if we can find a websocket server
    # local port (should we just source this from the config?)

    return 0
