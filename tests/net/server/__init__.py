"""
Test HTTP server interactions.
"""

# built-in
import asyncio
from typing import Any

# module under test
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.server import RuntimepyServerConnection
from runtimepy.net.server.websocket import RuntimepyWebsocketConnection
from runtimepy.net.tcp.http import HttpConnection

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


async def runtimepy_http_query_peer(app: AppInfo) -> None:
    """Test querying a peer program's web application."""

    port: int = 0

    # Try to find peer's HTTP server.
    if "proc1" in app.peers:
        peer = app.peers["proc1"]
        await peer.peer_config_event.wait()
        for port in peer.peer_config["ports"]:  # type: ignore
            if port["name"] == "runtimepy_http_server":  # type: ignore
                port = port["port"]  # type: ignore
                break

    if port:
        conn = await HttpConnection.create_connection(
            host="localhost", port=port
        )
        async with conn.process_then_disable(stop_sig=app.stop):
            await conn.request(RequestHeader(target="/app.html"))


async def runtimepy_http_client_server(
    app: AppInfo,
    client: RuntimepyServerConnection,
    server: RuntimepyServerConnection,
) -> None:
    """Test HTTP client and server interactions."""

    # Add another path to server.
    server.add_path(resource("http"), front=True)

    env = "connection_metrics_poller"
    env_path = f"/json/environments/{env}"

    # Make requests in parallel.
    await asyncio.gather(
        *(
            runtimepy_http_query_peer(app),
            # Application.
            client.request(RequestHeader(target="/")),
            client.request(RequestHeader(target="/app.html")),
            client.request(RequestHeader(target="/app.html")),
            client.request(RequestHeader(target="/index.html")),
            client.request(RequestHeader(target="/test_json.html")),
            client.request(RequestHeader(target="/landing_page.html")),
            client.request(RequestHeader(target="/README.md")),
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
            # Send commands.
            client.request_json(RequestHeader(method="POST", target="/")),
            client.request_json(RequestHeader(method="POST", target="/a")),
            client.request_json(RequestHeader(method="POST", target="/a/b/c")),
            client.request_json(
                RequestHeader(method="POST", target="/app/help")
            ),
            client.request_json(
                RequestHeader(method="POST", target="/app/toggle")
            ),
            client.request_json(
                RequestHeader(method="POST", target="/app/toggle/asdf")
            ),
            client.request_json(
                RequestHeader(method="POST", target="/app/toggle/paused")
            ),
            client.request_json(
                RequestHeader(method="POST", target="/app/toggle/paused")
            ),
            client.request_json(
                RequestHeader(method="POST", target="/sample1/custom/asdf")
            ),
            client.request_json(
                RequestHeader(method="POST", target="/struct2/custom/poll")
            ),
            client.request_json(
                RequestHeader(method="POST", target="/struct2/custom/poll/5")
            ),
            client.request_json(
                RequestHeader(
                    method="POST", target="/struct2/custom/poll/5/0.01"
                )
            ),
            client.request_json(
                RequestHeader(
                    method="POST", target="/sample1/custom/test_command"
                )
            ),
        )
    )
