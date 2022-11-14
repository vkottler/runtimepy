"""
A module implementing a WebSocket connection interface.
"""

from __future__ import annotations

# built-in
import asyncio as _asyncio
from typing import Awaitable as _Awaitable
from typing import Callable as _Callable
from typing import Union as _Union

# third-party
from websockets.client import (
    WebSocketClientProtocol as _WebSocketClientProtocol,
)
from websockets.exceptions import ConnectionClosed as _ConnectionClosed
from websockets.server import (
    WebSocketServerProtocol as _WebSocketServerProtocol,
)

BinaryMessage = _Union[bytes, bytearray, memoryview]
ConnectionInit = _Callable[["WebsocketConnection"], _Awaitable[bool]]


class WebsocketConnection:
    """A simple websocket connection interface."""

    def __init__(
        self,
        protocol: _Union[_WebSocketClientProtocol, _WebSocketServerProtocol],
    ) -> None:
        """Initialize this connection."""

        self.protocol = protocol
        self.enabled = True
        self.text_messages: _asyncio.Queue[str] = _asyncio.Queue()
        self.binary_messages: _asyncio.Queue[BinaryMessage] = _asyncio.Queue()

    def send_text(self, data: str) -> None:
        """Enqueue a text message to send."""
        self.text_messages.put_nowait(data)

    def send_binary(self, data: BinaryMessage) -> None:
        """Enqueue a binary message tos end."""
        self.binary_messages.put_nowait(data)

    async def process_text(self, data: str) -> bool:
        """Process a text frame."""
        del data
        return True

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""
        del data
        return True

    async def _process_read(self) -> None:
        """Process incoming messages while this connection is active."""

        while self.enabled:
            try:
                message = await self.protocol.recv()

                if isinstance(message, str):
                    self.enabled = await _asyncio.shield(
                        self.process_text(message)
                    )
                else:
                    self.enabled = await _asyncio.shield(
                        self.process_binary(message)
                    )
            except (_ConnectionClosed, _asyncio.CancelledError):
                self.enabled = False

    async def _process_write_text(self) -> None:
        """Process outgoing text messages."""

        while self.enabled:
            try:
                await self.protocol.send(await self.text_messages.get())
                self.text_messages.task_done()
            except _asyncio.CancelledError:
                self.enabled = False

    async def _process_write_binary(self) -> None:
        """Process outgoing binary messages."""

        while self.enabled:
            try:
                await self.protocol.send(await self.binary_messages.get())
                self.binary_messages.task_done()
            except _asyncio.CancelledError:
                self.enabled = False

    async def process(self) -> None:
        """
        Process tasks for this connection while the connection is active.
        """

        _, pending = await _asyncio.wait(
            [
                _asyncio.create_task(self._process_read()),
                _asyncio.create_task(self._process_write_text()),
                _asyncio.create_task(self._process_write_binary()),
            ],
            return_when=_asyncio.FIRST_COMPLETED,
        )

        self.enabled = False
        for task in pending:
            task.cancel()
            await task

        await self.protocol.close()


def server_handler(
    init: ConnectionInit,
) -> _Callable[[_WebSocketServerProtocol], _Awaitable[None]]:
    """
    A wrapper for passing in a websocket handler and initializing a connection.
    """

    async def _handler(protocol: _WebSocketServerProtocol) -> None:
        """A handler that runs the callers initialization function."""
        conn = WebsocketConnection(protocol)
        if await init(conn):
            await conn.process()

    return _handler
