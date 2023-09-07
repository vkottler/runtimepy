"""
A module implementing a network-connection interface.
"""

# built-in
from abc import ABC as _ABC
import asyncio as _asyncio
from contextlib import suppress as _suppress
from typing import List as _List
from typing import Optional as _Optional
from typing import Union as _Union

# third-party
from vcorelib.asyncio import log_exceptions as _log_exceptions
from vcorelib.logging import LoggerMixin as _LoggerMixin
from vcorelib.logging import LoggerType as _LoggerType

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.metrics import ConnectionMetrics
from runtimepy.mixins.environment import ChannelEnvironmentMixin
from runtimepy.primitives.byte_order import DEFAULT_BYTE_ORDER, ByteOrder

BinaryMessage = _Union[bytes, bytearray, memoryview]


class Connection(_LoggerMixin, ChannelEnvironmentMixin, _ABC):
    """A connection interface."""

    uses_text_tx_queue = True
    uses_binary_tx_queue = True

    byte_order: ByteOrder = DEFAULT_BYTE_ORDER

    def __init__(
        self,
        logger: _LoggerType,
        env: ChannelEnvironment = None,
        add_metrics: bool = True,
    ) -> None:
        """Initialize this connection."""

        _LoggerMixin.__init__(self, logger=logger)
        self._enabled = True

        # A queue for out-going text messages. Connections that don't use
        # this can set 'uses_text_tx_queue' to False to avoid scheduling a
        # task for it.
        self._text_messages: _asyncio.Queue[str] = _asyncio.Queue()
        self.tx_text_hwm: int = 0

        # A queue for out-going binary messages. Connections that don't use
        # this can set 'uses_binary_tx_queue' to False to avoid scheduling a
        # task for it.
        self._binary_messages: _asyncio.Queue[BinaryMessage] = _asyncio.Queue()
        self.tx_binary_hwm: int = 0

        self._tasks: _List[_asyncio.Task[None]] = []
        self.initialized = _asyncio.Event()
        self.disabled_event = _asyncio.Event()

        self.metrics = ConnectionMetrics()

        ChannelEnvironmentMixin.__init__(self, env=env)
        if add_metrics:
            self.register_connection_metrics(self.metrics)

        self.init()

    def init(self) -> None:
        """Initialize this instance."""

    def log_metrics(self, label: str = "conn") -> None:
        """Log connection metrics."""
        self.logger.info("(%s) tx: %s", label, self.metrics.tx)
        self.logger.info("(%s) rx: %s", label, self.metrics.rx)

    async def async_init(self) -> bool:
        """A runtime initialization routine (executes during 'process')."""
        return True

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
        self.tx_text_hwm = max(self.tx_text_hwm, self._text_messages.qsize())

    def send_binary(self, data: BinaryMessage) -> None:
        """Enqueue a binary message tos end."""

        self._binary_messages.put_nowait(data)
        self.tx_binary_hwm = max(
            self.tx_binary_hwm, self._binary_messages.qsize()
        )

    @property
    def disabled(self) -> bool:
        """Determine if this connection is disabled."""
        return not self._enabled

    def disable_extra(self) -> None:
        """Additional tasks to perform when disabling."""

    def disable(self, reason: str) -> None:
        """Disable this connection."""

        if self._enabled:
            self.logger.info("Disabling connection: '%s'.", reason)
            self.disable_extra()
            self._enabled = False

            # Cancel tasks.
            for task in self._tasks:
                if not task.done():
                    task.cancel()

            # Signal that this connection has been disabled.
            self.disabled_event.set()

    async def _wait_sig(self, stop_sig: _asyncio.Event) -> None:
        """Disable the connection if a stop signal gets set."""
        await stop_sig.wait()
        self.disable("stop signal")

    async def _async_init(self) -> None:
        """Run this connection's initialization routine."""

        if not await self.async_init():
            self.disable("init failed")
        else:
            self.logger.info("Initialized.")
        self.initialized.set()

    async def process(self, stop_sig: _asyncio.Event = None) -> None:
        """
        Process tasks for this connection while the connection is active.
        """

        self._tasks = [
            _asyncio.create_task(self._process_read()),
            _asyncio.create_task(self._async_init()),
        ]

        if self.uses_text_tx_queue:
            self._tasks.append(
                _asyncio.create_task(self._process_write_text())
            )
        if self.uses_binary_tx_queue:
            self._tasks.append(
                _asyncio.create_task(self._process_write_binary())
            )

        # Allow a stop signal to also disable the connection.
        if stop_sig is not None:
            self._tasks.append(_asyncio.create_task(self._wait_sig(stop_sig)))

        await _asyncio.wait(self._tasks, return_when=_asyncio.ALL_COMPLETED)

        # Ensure that tasks have their exceptions retrieved.
        _log_exceptions(self._tasks, self.logger)

        await self.close()

    async def _process_read(self) -> None:
        """Process incoming messages while this connection is active."""

        with _suppress(KeyboardInterrupt):
            while self._enabled:
                # Attempt to get the next message.
                message = await self._await_message()
                result = False

                if message is not None:
                    # Process a text or binary message.
                    if isinstance(message, str):
                        result = await self.process_text(message)
                    else:
                        result = await self.process_binary(message)

                # If we failed to read a message, disable.
                if not result:
                    self.disable("read processing error")

    async def _process_write_text(self) -> None:
        """Process outgoing text messages."""

        queue: _asyncio.Queue[str] = self._text_messages

        while self._enabled:
            # Attempt to get the next message.
            data = await queue.get()

            # Process it.
            if data is not None:
                await self._send_text_message(data)
                queue.task_done()

    async def _process_write_binary(self) -> None:
        """Process outgoing binary messages."""

        queue: _asyncio.Queue[BinaryMessage] = self._binary_messages

        while self._enabled:
            # Attempt to get the next message.
            data = await queue.get()

            # Process it.
            if data is not None:
                await self._send_binay_message(data)
                queue.task_done()


class EchoConnection(Connection):
    """A connection that just echoes what it was sent."""

    async def process_text(self, data: str) -> bool:
        """Process a text frame."""
        self.send_text(data)
        return True

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""
        self.send_binary(data)
        return True


class NullConnection(Connection):
    """A connection that doesn't do anything with incoming data."""

    async def process_text(self, data: str) -> bool:
        """Process a text frame."""
        return True

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""
        return True
