"""
Test the 'net.stream' module.
"""

# built-in
import asyncio

# module under test
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.stream import StringMessageConnection
from runtimepy.net.stream.json import JsonMessageConnection


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


async def json_client_test(client: JsonMessageConnection) -> int:
    """Test a single JSON client."""

    client.send_json({})

    await client.wait_json({})

    assert await client.wait_json({"unknown": 0, "command": 1}) == {
        "keys_ignored": ["command", "unknown"]
    }

    # Test loopback.
    assert await client.loopback()
    assert await client.loopback(data={"a": 1, "b": 2, "c": 3})

    return 0


async def json_test(app: AppInfo) -> int:
    """Test JSON clients in parallel."""

    return sum(
        await asyncio.gather(
            *[
                json_client_test(client)
                for client in [
                    app.single(
                        pattern="udp_json_client", kind=JsonMessageConnection
                    ),
                    app.single(pattern="tcp_json", kind=JsonMessageConnection),
                    app.single(
                        pattern="websocket_json", kind=JsonMessageConnection
                    ),
                ]
            ]
        )
    )
