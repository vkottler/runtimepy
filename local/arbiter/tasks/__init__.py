"""
A module for runtimepy arbiter applications.
"""

# built-in
import asyncio

# internal
from runtimepy.net import Connection
from runtimepy.net.arbiter import AppInfo


async def noop1(app: AppInfo) -> int:
    """An app that doesn't do much."""

    app.logger.info("I ran!")
    return 0


async def noop2(app: AppInfo) -> int:
    """An app that doesn't do much."""

    app.logger.info("I ran!")
    return 1


async def gui(app: AppInfo) -> int:
    """Run a channel GUI for application connections."""

    print(app)

    return 0


async def test(app: AppInfo) -> int:
    """A network application that doesn't do anything."""

    while not app.stop.is_set():
        for conn in app.search(pattern="client", kind=Connection):
            for _ in range(100):
                conn.send_text("Hello, world!")

        await asyncio.sleep(0.1)

    return 0
