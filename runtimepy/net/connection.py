"""
A module implementing a network-connection interface.
"""

# built-in
from abc import ABC as _ABC
import asyncio as _asyncio
from typing import Awaitable as _Awaitable
from typing import List as _List
from typing import Optional as _Optional
from typing import TypeVar as _TypeVar
from typing import Union as _Union

# third-party
from vcorelib.asyncio import log_exceptions as _log_exceptions
from vcorelib.logging import LoggerMixin as _LoggerMixin
from vcorelib.logging import LoggerType as _LoggerType

BinaryMessage = _Union[bytes, bytearray, memoryview]
T = _TypeVar("T")


class Connection(_LoggerMixin, _ABC):
    """A connection interface."""

    def __init__(self, logger: _LoggerType) -> None:
        """Initialize this connection."""

        super().__init__(logger=logger)
        self._enabled = True
        self._text_messages: _asyncio.Queue[str] = _asyncio.Queue()
        self._binary_messages: _asyncio.Queue[BinaryMessage] = _asyncio.Queue()
        self._tasks: _List[_asyncio.Task[None]] = []
        self.init()

    def init(self) -> None:
        """Initialize this instance."""

    async def process_text(self, data: str) -> bool:
        """Process a text frame."""
        raise NotImplementedError

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""
        raise NotImplementedError

    async def _await_message(self) -> _Optional[_Union[BinaryMessage, str]]:
        """Await the next message. Return None on error or failure."""
        raise NotImplementedError

    async def _send_text_message(self, data: str) -> None:
        """Send a text message."""
        raise NotImplementedError

    async def _send_binay_message(self, data: BinaryMessage) -> None:
        """Send a binary message."""
        raise NotImplementedError

    async def close(self) -> None:
        """Close this connection."""

    def send_text(self, data: str) -> None:
        """Enqueue a text message to send."""
        self._text_messages.put_nowait(data)

    def send_binary(self, data: BinaryMessage) -> None:
        """Enqueue a binary message tos end."""
        self._binary_messages.put_nowait(data)

    @property
    def disabled(self) -> bool:
        """Determine if this connection is disabled."""
        return not self._enabled

    def disable(self, reason: str) -> None:
        """Disable this connection."""

        if self._enabled:
            self.logger.info("Disabling connection: '%s'.", reason)
            self._enabled = False

            # Cancel tasks.
            for task in self._tasks:
                if not task.done():
                    task.cancel()

    async def _wait_sig(self, stop_sig: _asyncio.Event) -> None:
        """Disable the connection if a stop signal gets set."""
        await stop_sig.wait()
        self.disable("stop signal")

    async def process(self, stop_sig: _asyncio.Event = None) -> None:
        """
        Process tasks for this connection while the connection is active.
        """

        self._tasks = [
            _asyncio.create_task(self._process_read()),
            _asyncio.create_task(self._process_write_text()),
            _asyncio.create_task(self._process_write_binary()),
        ]

        # Allow a stop signal to also disable the connection.
        if stop_sig is not None:
            self._tasks.append(_asyncio.create_task(self._wait_sig(stop_sig)))

        await _asyncio.wait(self._tasks, return_when=_asyncio.ALL_COMPLETED)

        # Ensure that tasks have their exceptions retrieved.
        _log_exceptions(self._tasks, self.logger)

        await self.close()

    async def _process_read(self) -> None:
        """Process incoming messages while this connection is active."""

        while self._enabled:
            # Attempt to get the next message.
            message = await self._cancelled_handler(
                self._await_message(), "reading cancelled"
            )
            result = False

            if message is not None:
                # Process a text message.
                if isinstance(message, str):
                    result = await _asyncio.shield(self.process_text(message))

                # Process a binary message.
                else:
                    result = await _asyncio.shield(
                        self.process_binary(message)
                    )

            # If we failed to read a message, disable.
            if not result:
                self.disable("read processing error")

    async def _process_write_text(self) -> None:
        """Process outgoing text messages."""

        cancel_msg = "writing cancelled"
        queue: _asyncio.Queue[str] = self._text_messages

        while self._enabled:
            # Attempt to get the next message.
            data = await self._cancelled_handler(queue.get(), cancel_msg)

            # Process it.
            if data is not None:
                await self._cancelled_handler(
                    self._send_text_message(data), cancel_msg
                )
                queue.task_done()

    async def _process_write_binary(self) -> None:
        """Process outgoing binary messages."""

        cancel_msg = "writing cancelled"
        queue: _asyncio.Queue[BinaryMessage] = self._binary_messages

        while self._enabled:
            # Attempt to get the next message.
            data = await self._cancelled_handler(queue.get(), cancel_msg)

            # Process it.
            if data is not None:
                await self._cancelled_handler(
                    self._send_binay_message(data), cancel_msg
                )
                queue.task_done()

    async def _cancelled_handler(
        self, task: _Awaitable[T], disable_message: str = None
    ) -> _Optional[T]:
        """
        A simple wrapper for handling cancellations from the event loop. Pass
        a disable message if the cancellation should disable the connection.
        """

        result = None
        try:
            result = await task
        except _asyncio.CancelledError:
            if disable_message is not None:
                self.disable(disable_message)
        return result
