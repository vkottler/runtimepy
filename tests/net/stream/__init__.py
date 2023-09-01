"""
Test the 'net.stream' module.
"""

# built-in
import asyncio

# module under test
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.stream import StringMessageConnection


async def stream_test(app: AppInfo) -> int:
    """A network application that doesn't do anything."""

    count = 0
    for client in app.search(
        pattern="message_client", kind=StringMessageConnection
    ):
        for _ in range(100):
            client.send_message_str("Hello, world!")
        count += 1

    await asyncio.sleep(0.1)

    assert count > 0
    return 0
