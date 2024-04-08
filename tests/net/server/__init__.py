"""
Test HTTP server interactions.
"""

# built-in
import asyncio
from typing import Any

# module under test
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.server import RuntimepyServerConnection
from runtimepy.net.server.websocket import RuntimepyWebsocketConnection

# internal
from tests.resources import resource


def send_ui(
    client: RuntimepyWebsocketConnection, name: str, data: Any
) -> None:
    """Send a UI message."""
    client.send_json({"ui": {"name": name, "event": data}})


async def runtimepy_websocket_client(
    client: RuntimepyWebsocketConnection,
) -> None:
    """Test client interactions via WebSocket."""

    send_ui(client, "test", {"a": 1, "b": 2, "c": 3})

    time = 0.0
    period = 0.05

    for idx in range(3):
        send_ui(client, f"sample{idx}", {"kind": "asdf"})
        send_ui(client, f"sample{idx}", {"kind": "init"})
        send_ui(client, f"sample{idx}", {"kind": "tab.shown"})
        send_ui(client, f"sample{idx}", {"kind": "tab.hidden"})
        send_ui(client, f"sample{idx}", {"kind": "command", "value": "help"})

        # Trigger some telemetry sending.
        send_ui(client, f"wave{idx}", {"kind": "init"})
        send_ui(client, f"wave{idx}", {"kind": "tab.shown"})

        # Drive the UI forward.
        for _ in range(5):
            await asyncio.sleep(period)
            client.send_json({"ui": {"time": time}})
            time += period

        send_ui(client, f"wave{idx}", {"kind": "tab.hidden"})


async def runtimepy_http_client_server(
    client: RuntimepyServerConnection, server: RuntimepyServerConnection
) -> None:
    """Test HTTP client and server interactions."""

    # Add another path to server.
    server.add_path(resource("http"), front=True)

    env = "connection_metrics_poller"
    env_path = f"/json/environments/{env}"

    # Make requests in parallel.
    await asyncio.gather(
        *(
            # Application.
            client.request(RequestHeader(target="/")),
            client.request(RequestHeader(target="/index.html")),
            # Files from file-system.
            client.request(RequestHeader(target="/sample.json")),
            client.request(RequestHeader(target="/manifest.yaml")),
            client.request(RequestHeader(target="/pyproject.toml")),
            # favicon.ico.
            client.request(RequestHeader(target="/favicon.ico")),
            # JSON queries.
            client.request_json(RequestHeader(target="/json")),
            client.request_json(RequestHeader(target="/json//////")),
            client.request_json(RequestHeader(target="/json/a")),
            client.request_json(RequestHeader(target="/json/test")),
            client.request_json(RequestHeader(target="/json/test/a")),
            client.request_json(RequestHeader(target="/json/test/a/b")),
            client.request_json(RequestHeader(target="/json/test/d")),
            client.request_json(RequestHeader(target=env_path)),
            client.request_json(RequestHeader(target=f"{env_path}/values")),
        )
    )
