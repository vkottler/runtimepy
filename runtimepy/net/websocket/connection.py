"""
A module implementing a WebSocket connection interface.
"""

from __future__ import annotations

# built-in
from typing import Awaitable as _Awaitable
from typing import Callable as _Callable
from typing import Optional as _Optional
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# third-party
from websockets.client import (
    WebSocketClientProtocol as _WebSocketClientProtocol,
)
from websockets.exceptions import ConnectionClosed as _ConnectionClosed
from websockets.server import (
    WebSocketServerProtocol as _WebSocketServerProtocol,
)

# internal
from runtimepy.net.connection import BinaryMessage, Connection

T = _TypeVar("T", bound="WebsocketConnection")
ConnectionInit = _Callable[[T], _Awaitable[bool]]


class WebsocketConnection(Connection):
    """A simple websocket connection interface."""

    def __init__(
        self,
        protocol: _Union[_WebSocketClientProtocol, _WebSocketServerProtocol],
    ) -> None:
        """Initialize this connection."""

        self.protocol = protocol
        super().__init__(self.protocol.logger)

    async def _await_message(self) -> _Optional[_Union[BinaryMessage, str]]:
        """Await the next message. Return None on error or failure."""

        try:
            message = await self.protocol.recv()
        except _ConnectionClosed:
            self._logger.info("Connection closed.")
            message = None

        return message

    async def _send_text_message(self, data: str) -> None:
        """Send a text message."""
        await self.protocol.send(data)

    async def _send_binay_message(self, data: BinaryMessage) -> None:
        """Send a binary message."""
        await self.protocol.send(data)

    async def close(self) -> None:
        """Close this connection."""
        await self.protocol.close()


def server_handler(
    init: ConnectionInit[T], cls: _Type[T]
) -> _Callable[[_WebSocketServerProtocol], _Awaitable[None]]:
    """
    A wrapper for passing in a websocket handler and initializing a connection.
    """

    async def _handler(protocol: _WebSocketServerProtocol) -> None:
        """A handler that runs the callers initialization function."""
        conn = cls(protocol)
        if await init(conn):
            await conn.process()

    return _handler
