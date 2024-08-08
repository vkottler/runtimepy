"""
A module implementing a base tftp (RFC 1350) connection interface.
"""

# built-in
import asyncio
from contextlib import AsyncExitStack
from io import BytesIO
import logging
from pathlib import Path
from typing import BinaryIO, Callable

# third-party
from vcorelib.math import metrics_time_ns

# internal
from runtimepy.net import IpHost
from runtimepy.net.udp.connection import UdpConnection
from runtimepy.net.udp.tftp.endpoint import TftpEndpoint
from runtimepy.net.udp.tftp.enums import (
    DEFAULT_MODE,
    TftpErrorCode,
    TftpOpCode,
    encode_filename_mode,
    parse_filename_mode,
)
from runtimepy.net.util import IpHostTuplelike, normalize_host
from runtimepy.primitives import Double, Uint16

REEMIT_PERIOD_S = 0.20
DEFAULT_TIMEOUT_S = 1.0

TftpErrorHandler = Callable[[TftpErrorCode, str, tuple[str, int]], None]


class BaseTftpConnection(UdpConnection):
    """A class implementing a basic tftp interface."""

    log_alias = "TFTP"

    _path: Path

    default_auto_restart = True
    should_connect = False

    def set_root(self, path: Path) -> None:
        """Set a new root path for this instance."""

        self._path = path
        for endpoint in self._endpoints.values():
            endpoint.set_root(self._path)
        self.logger.info("Set root directory to '%s'.", self._path)

    @property
    def path(self) -> Path:
        """Get this connection's root path."""
        return self._path

    def init(self) -> None:
        """Initialize this instance."""

        super().init()

        # Path to serve files from.
        self._path = Path()

        TftpOpCode.register_enum(self.env.enums)
        TftpErrorCode.register_enum(self.env.enums)

        self.opcode = Uint16(time_source=metrics_time_ns)
        self.env.channel("opcode", self.opcode, enum="TftpOpCode")

        self.block_number = Uint16(time_source=metrics_time_ns)
        self.env.channel("block_number", self.block_number)

        self.error_code = Uint16(time_source=metrics_time_ns)
        self.env.channel("error_code", self.error_code, enum="TftpErrorCode")
        self.error_handlers: list[TftpErrorHandler] = []

        self.endpoint_period = Double(value=REEMIT_PERIOD_S)
        self.env.channel(
            "reemit_period_s",
            self.endpoint_period,
            commandable=True,
            description="Time between packet re-transmissions.",
        )
        self.endpoint_timeout = Double(value=DEFAULT_TIMEOUT_S)
        self.env.channel(
            "timeout_s",
            self.endpoint_timeout,
            commandable=True,
            description="A timeout used for each step.",
        )

        # Message parsers.
        self.handlers = {
            TftpOpCode.RRQ.value: self._handle_rrq,
            TftpOpCode.WRQ.value: self._handle_wrq,
            TftpOpCode.DATA.value: self._handle_data,
            TftpOpCode.ACK.value: self._handle_ack,
            TftpOpCode.ERROR.value: self._handle_error,
        }

        def data_sender(
            block: int, data: bytes, addr: IpHostTuplelike
        ) -> None:
            """Send data via this connection instance."""

            self.send_data(block, data, addr=addr)

        self.data_sender = data_sender

        def ack_sender(block: int, addr: IpHostTuplelike) -> None:
            """Send an ack via this connection."""

            self.send_ack(block=block, addr=addr)

        self.ack_sender = ack_sender

        def error_sender(
            error_code: TftpErrorCode,
            message: str,
            addr: IpHostTuplelike,
        ) -> None:
            """Sen an error via this connection."""

            self.send_error(error_code, message, addr=addr)

        self.error_sender = error_sender

        self._endpoints: dict[IpHost, TftpEndpoint] = {}
        self._awaiting_first_ack: dict[str, TftpEndpoint] = {}
        self._awaiting_first_block: dict[str, TftpEndpoint] = {}
        # self._self = self.endpoint(self.local_address)

    async def _await_first_ack(
        self,
        stack: AsyncExitStack,
        addr: IpHostTuplelike = None,
    ) -> tuple[TftpEndpoint, asyncio.Event]:
        """Set up an endpoint to wait for an initial ack from a server."""

        endpoint = self.endpoint(addr)
        await stack.enter_async_context(endpoint.lock)
        event = asyncio.Event()
        endpoint.awaiting_acks[0] = event
        self._awaiting_first_ack[endpoint.addr.hostname] = endpoint
        return endpoint, event

    async def _await_first_block(
        self,
        stack: AsyncExitStack,
        addr: IpHostTuplelike = None,
    ) -> tuple[TftpEndpoint, asyncio.Event]:
        """Set up an endpoint to wait for an initial block from a server."""

        endpoint = self.endpoint(addr)
        await stack.enter_async_context(endpoint.lock)
        event = asyncio.Event()
        endpoint.awaiting_blocks[1] = event
        self._awaiting_first_block[endpoint.addr.hostname] = endpoint
        return endpoint, event

    def endpoint(self, addr: IpHostTuplelike = None) -> TftpEndpoint:
        """Lookup an endpoint instance from an address."""

        if addr is None:
            addr = self.remote_address

        assert addr is not None
        addr = normalize_host(*addr)

        if addr not in self._endpoints:
            self._endpoints[addr] = TftpEndpoint(
                self._path,
                self.logger,
                addr,
                self.data_sender,
                self.ack_sender,
                self.error_sender,
                self.endpoint_period,
                self.endpoint_timeout,
            )

        return self._endpoints[addr]

    def send_rrq(
        self,
        filename: str,
        mode: str = DEFAULT_MODE,
        addr: IpHostTuplelike = None,
    ) -> None:
        """Send a read request."""

        self._send_message(
            TftpOpCode.RRQ, encode_filename_mode(filename, mode), addr=addr
        )

    def send_wrq(
        self,
        filename: str,
        mode: str = DEFAULT_MODE,
        addr: IpHostTuplelike = None,
    ) -> None:
        """Send a write request."""

        self._send_message(
            TftpOpCode.WRQ, encode_filename_mode(filename, mode), addr=addr
        )

    def send_data(
        self,
        block: int,
        data: bytes,
        addr: IpHostTuplelike = None,
    ) -> None:
        """Send a data message."""

        self.block_number.value = block
        self._send_message(
            TftpOpCode.DATA, bytes(self.block_number) + data, addr=addr
        )

    def send_ack(self, block: int = 0, addr: IpHostTuplelike = None) -> None:
        """Send a data message."""

        self.block_number.value = block
        self._send_message(TftpOpCode.ACK, bytes(self.block_number), addr=addr)

    def send_error(
        self,
        error_code: TftpErrorCode,
        message: str,
        addr: IpHostTuplelike = None,
    ) -> None:
        """Send a data message."""

        with BytesIO() as stream:
            self.error_code.value = error_code.value
            self.error_code.to_stream(stream)

            stream.write(message.encode())
            stream.write(b"\x00")

            self._send_message(TftpOpCode.ERROR, stream.getvalue(), addr=addr)

        # Log errors sent.
        endpoint = self.endpoint(addr)
        self.governed_log(
            endpoint.log_limiter,
            "Sent error '%s: %s' to %s.",
            error_code.name,
            message,
            endpoint,
            level=logging.WARNING,
        )

    def _send_message(
        self,
        opcode: TftpOpCode,
        data: bytes,
        addr: IpHostTuplelike = None,
    ) -> None:
        """Send a tftp message."""

        with BytesIO() as stream:
            # Set opcode.
            self.opcode.value = opcode.value
            self.opcode.to_stream(stream)

            # Encode message.
            stream.write(data)

            self.sendto(stream.getvalue(), addr=addr)

    async def _handle_rrq(
        self, stream: BinaryIO, addr: tuple[str, int]
    ) -> None:
        """Handle a read request."""

        task = self.endpoint(addr).handle_read_request(
            *parse_filename_mode(stream)
        )
        if task is not None:
            self._conn_tasks.append(task)

    async def _handle_wrq(
        self, stream: BinaryIO, addr: tuple[str, int]
    ) -> None:
        """Handle a write request."""

        task = self.endpoint(addr).handle_write_request(
            *parse_filename_mode(stream)
        )
        if task is not None:
            self._conn_tasks.append(task)

    async def _handle_data(
        self, stream: BinaryIO, addr: tuple[str, int]
    ) -> None:
        """Handle a data message."""

        endpoint = self.endpoint(addr)
        block = self._read_block_number(stream)

        # Check if we're currently waiting for an initial block.
        hostname = endpoint.addr.hostname
        if block == 1 and hostname in self._awaiting_first_block:
            to_update = self._awaiting_first_block[hostname]
            del self._awaiting_first_block[hostname]
            self._endpoints[endpoint.addr] = to_update
            endpoint = to_update.update_from_other(endpoint)

        endpoint.handle_data(block, stream.read())

    async def _handle_ack(
        self, stream: BinaryIO, addr: tuple[str, int]
    ) -> None:
        """Handle an acknowledge message."""

        endpoint = self.endpoint(addr)
        block = self._read_block_number(stream)

        # Check if we're currently waiting for an initial acknowledgement. This
        # will come from the same host but a different port, so update
        # references when this is detected.
        hostname = endpoint.addr.hostname
        if block == 0 and hostname in self._awaiting_first_ack:
            to_update = self._awaiting_first_ack[hostname]
            del self._awaiting_first_ack[hostname]
            self._endpoints[endpoint.addr] = to_update
            endpoint = to_update.update_from_other(endpoint)

        endpoint.handle_ack(block)

    def _read_block_number(self, stream: BinaryIO) -> int:
        """Read block number from the stream."""
        return self.block_number.from_stream(stream)

    async def _handle_error(
        self, stream: BinaryIO, addr: tuple[str, int]
    ) -> None:
        """Handle an error message."""

        # Update underlying primitive.
        error_code = TftpErrorCode(self.error_code.from_stream(stream))
        message = stream.read().decode()

        # Call extra error handlers.
        for handler in self.error_handlers:
            handler(error_code, message, addr)

        self.endpoint(addr).handle_error(error_code, message)

    async def process_datagram(
        self, data: bytes, addr: tuple[str, int]
    ) -> bool:
        """Process a datagram."""

        with BytesIO(data) as stream:
            self.opcode.from_stream(stream)
            code: int = self.opcode.value
            if code in self.handlers:
                await self.handlers[code](stream, addr)
            else:
                msg = f"Unknown opcode {code}"
                self.send_error(TftpErrorCode.ILLEGAL_OPERATION, msg)
                self.logger.error("%s from %s:%d.", msg, addr[0], addr[1])

        return True
