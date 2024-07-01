"""
A module implementing a base tftp (RFC 1350) connection interface.
"""

# built-in
from io import BytesIO
import logging
from pathlib import Path
from typing import BinaryIO, Union

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
from runtimepy.primitives import Uint16


class BaseTftpConnection(UdpConnection):
    """A class implementing a basic tftp interface."""

    log_alias = "TFTP"

    _path: Path

    default_auto_restart = True

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

        # Message parsers.
        self.handlers = {
            TftpOpCode.RRQ.value: self._handle_rrq,
            TftpOpCode.WRQ.value: self._handle_wrq,
            TftpOpCode.DATA.value: self._handle_data,
            TftpOpCode.ACK.value: self._handle_ack,
            TftpOpCode.ERROR.value: self._handle_error,
        }

        def data_sender(
            block: int, data: bytes, addr: Union[IpHost, tuple[str, int]]
        ) -> None:
            """Send data via this connection instance."""

            self.send_data(block, data, addr=addr)

        self.data_sender = data_sender

        def ack_sender(
            block: int, addr: Union[IpHost, tuple[str, int]]
        ) -> None:
            """Send an ack via this connection."""

            self.send_ack(block=block, addr=addr)

        self.ack_sender = ack_sender

        def error_sender(
            error_code: TftpErrorCode,
            message: str,
            addr: Union[IpHost, tuple[str, int]],
        ) -> None:
            """Sen an error via this connection."""

            self.send_error(error_code, message, addr=addr)

        self.error_sender = error_sender

        self._endpoints: dict[str, TftpEndpoint] = {}
        # self._self = self.endpoint(self.local_address)

    def endpoint(
        self, addr: Union[IpHost, tuple[str, int]] = None
    ) -> TftpEndpoint:
        """Lookup an endpoint instance from an address."""

        if addr is None:
            addr = self.remote_address

        assert addr is not None
        key = f"{addr[0]}:{addr[1]}"

        if key not in self._endpoints:
            self._endpoints[key] = TftpEndpoint(
                self._path,
                self.logger,
                addr,
                self.data_sender,
                self.ack_sender,
                self.error_sender,
            )

        return self._endpoints[key]

    def send_rrq(
        self,
        filename: str,
        mode: str = DEFAULT_MODE,
        addr: Union[IpHost, tuple[str, int]] = None,
    ) -> None:
        """Send a read request."""

        self._send_message(
            TftpOpCode.RRQ, encode_filename_mode(filename, mode), addr=addr
        )

    def send_wrq(
        self,
        filename: str,
        mode: str = DEFAULT_MODE,
        addr: Union[IpHost, tuple[str, int]] = None,
    ) -> None:
        """Send a write request."""

        self._send_message(
            TftpOpCode.WRQ, encode_filename_mode(filename, mode), addr=addr
        )

    def send_data(
        self,
        block: int,
        data: bytes,
        addr: Union[IpHost, tuple[str, int]] = None,
    ) -> None:
        """Send a data message."""

        self.block_number.value = block
        self._send_message(
            TftpOpCode.DATA, bytes(self.block_number) + data, addr=addr
        )

    def send_ack(
        self, block: int = 0, addr: Union[IpHost, tuple[str, int]] = None
    ) -> None:
        """Send a data message."""

        self.block_number.value = block
        self._send_message(TftpOpCode.ACK, bytes(self.block_number), addr=addr)

    def send_error(
        self,
        error_code: TftpErrorCode,
        message: str,
        addr: Union[IpHost, tuple[str, int]] = None,
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
        addr: Union[IpHost, tuple[str, int]] = None,
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

        block = self._read_block_number(stream)
        self.endpoint(addr).handle_data(block, stream.read())

    async def _handle_ack(
        self, stream: BinaryIO, addr: tuple[str, int]
    ) -> None:
        """Handle an acknowledge message."""

        self.endpoint(addr).handle_ack(self._read_block_number(stream))

    def _read_block_number(self, stream: BinaryIO) -> int:
        """Read block number from the stream."""
        return self.block_number.from_stream(stream)

    async def _handle_error(
        self, stream: BinaryIO, addr: tuple[str, int]
    ) -> None:
        """Handle an error message."""

        # Update underlying primitive.
        error_code = self.error_code.from_stream(stream)
        self.endpoint(addr).handle_error(
            TftpErrorCode(error_code), stream.read().decode()
        )

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
