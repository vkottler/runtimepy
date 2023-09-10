"""
Test the 'net.stream' module.
"""

# built-in
import asyncio

# third-party
from vcorelib.dict.codec import BasicDictCodec

# module under test
from runtimepy import PKG_NAME
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.stream import StringMessageConnection
from runtimepy.net.stream.json import JsonMessage, JsonMessageConnection

# internal
from tests.resources import SampleArbiterTask


async def stream_test(app: AppInfo) -> int:
    """A network application that doesn't do anything."""

    assert list(app.search_tasks(SampleArbiterTask))

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


async def json_client_find_file(client: JsonMessageConnection) -> None:
    """Test JSON-message client file finding."""

    file_result = await client.wait_json(
        {
            "find_file": {
                "path": "schemas",
                "parts": ["BitFields.yaml"],
                "package": PKG_NAME,
                "decode": True,
            }
        }
    )
    assert file_result["find_file"]["path"] is not None
    assert file_result["find_file"]["decoded"]["success"]
    assert file_result["find_file"]["decoded"]["data"]

    file_result = await client.wait_json(
        {
            "find_file": {
                "path": "schemas",
                "parts": ["not_a_file"],
                "package": PKG_NAME,
            }
        }
    )
    assert file_result["find_file"]["path"] is None


async def json_client_test(client: JsonMessageConnection) -> int:
    """Test a single JSON client."""

    client.send_json({})
    await client.wait_json({})

    client.stage_remote_log("Hello, world!")
    client.stage_remote_log("Hello, world! %d", 2)

    await json_client_find_file(client)

    assert await client.wait_json({"unknown": 0, "command": 1}) == {
        "keys_ignored": ["command", "unknown"]
    }

    codec = BasicDictCodec.create({"a": 1, "b": 2, "c": 3})
    client.send_json(codec)
    assert await client.wait_json(codec) == {"keys_ignored": ["a", "b", "c"]}

    # Should trigger decode error.
    client.send_message_str("{hello")

    # Test loopback.
    assert await client.loopback()
    assert await client.loopback(data={"a": 1, "b": 2, "c": 3})

    return 0


async def json_test(app: AppInfo) -> int:
    """Test JSON clients in parallel."""

    # Add typed handler for UDP server connection.
    udp_server = app.single(
        pattern="udp_json_server", kind=JsonMessageConnection
    )

    async def typed_handler(
        response: JsonMessage, data: BasicDictCodec
    ) -> None:
        """An example handler."""

        response["it_worked"] = True
        response.update(data.asdict())

    # Test handler.
    udp_server.typed_handler("test", BasicDictCodec, typed_handler)

    udp_client = app.single(
        pattern="udp_json_client", kind=JsonMessageConnection
    )

    result = await udp_client.wait_json({"test": {"a": 1, "b": 2, "c": 3}})
    result = result["test"]
    assert "it_worked" in result
    assert result["it_worked"] is True, result
    assert result["a"] == 1, result
    assert result["b"] == 2, result
    assert result["c"] == 3, result

    return sum(
        await asyncio.gather(
            *[
                json_client_test(client)
                for client in [
                    udp_client,
                    app.single(pattern="tcp_json", kind=JsonMessageConnection),
                    app.single(
                        pattern="websocket_json", kind=JsonMessageConnection
                    ),
                ]
            ]
        )
    )
