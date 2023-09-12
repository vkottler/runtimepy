"""
A module for testing application performance.
"""

# built-in
import asyncio

from runtimepy.net.arbiter import AppInfo

# internal
from runtimepy.net.stream.json import JsonMessageConnection


async def test(app: AppInfo) -> int:
    """A network application that doesn't do anything."""

    conns = list(app.search(pattern="client", kind=JsonMessageConnection))

    while not app.stop.is_set():
        for conn in conns:
            if not conn.disabled:
                for _ in range(100):
                    conn.send_json({"null": None})

        await asyncio.sleep(0.04)

    return 0
