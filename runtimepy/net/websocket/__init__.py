"""
A module aggregating all WebSocket-related interfaces.
"""

# internal
from runtimepy.net.websocket.connection import (
    EchoWebsocketConnection,
    NullWebsocketConnection,
    WebsocketConnection,
)

__all__ = [
    "WebsocketConnection",
    "EchoWebsocketConnection",
    "NullWebsocketConnection",
]
