"""
A module implementing a websocket server.
"""

from __future__ import annotations

# built-in
import asyncio as _asyncio
from typing import Union as _Union

# third-party
from websockets.exceptions import ConnectionClosed as _ConnectionClosed
from websockets.server import (
    WebSocketServerProtocol as _WebSocketServerProtocol,
)

BinaryMessage = _Union[bytes, bytearray, memoryview]


class WebsocketServer:
    """A simple websocket server implementation."""

    def __init__(self, protocol: _WebSocketServerProtocol) -> None:
        """Initialize this server."""

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

    async def process_read(self) -> None:
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

    async def process_write_text(self) -> None:
        """Process outgoing text messages."""

        while self.enabled:
            try:
                await self.protocol.send(await self.text_messages.get())
                self.text_messages.task_done()
            except _asyncio.CancelledError:
                self.enabled = False

    async def process_write_binary(self) -> None:
        """Process outgoing binary messages."""

        while self.enabled:
            try:
                await self.protocol.send(await self.binary_messages.get())
                self.binary_messages.task_done()
            except _asyncio.CancelledError:
                self.enabled = False

    async def process(self) -> None:
        """
        Process tasks for this server connection while the connection is
        active.
        """

        _, pending = await _asyncio.wait(
            [
                _asyncio.create_task(self.process_read()),
                _asyncio.create_task(self.process_write_text()),
                _asyncio.create_task(self.process_write_binary()),
            ],
            return_when=_asyncio.FIRST_COMPLETED,
        )

        self.enabled = False
        for task in pending:
            task.cancel()
            await task

        await self.protocol.close()
