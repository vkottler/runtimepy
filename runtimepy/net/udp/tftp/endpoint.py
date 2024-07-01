"""
A module implementing an interface for individual tftp endpoints.
"""

# built-in
import asyncio
from contextlib import AsyncExitStack, suppress
import logging
from pathlib import Path
from typing import BinaryIO, Callable, Optional, Union

# third-party
from vcorelib.asyncio.poll import repeat_until
from vcorelib.logging import LoggerMixin, LoggerType
from vcorelib.math import RateLimiter
from vcorelib.paths.info import FileInfo

# internal
from runtimepy.net import IpHost
from runtimepy.net.udp.tftp.enums import TftpErrorCode
from runtimepy.net.udp.tftp.io import tftp_chunks

TftpDataSender = Callable[[int, bytes, Union[IpHost, tuple[str, int]]], None]
TftpAckSender = Callable[[int, Union[IpHost, tuple[str, int]]], None]
TftpErrorSender = Callable[
    [TftpErrorCode, str, Union[IpHost, tuple[str, int]]], None
]

TFTP_MAX_BLOCK = 512

DALLY_PERIOD = 0.05
DALLY_TIMEOUT = 0.25


class TftpEndpoint(LoggerMixin):
    """A data structure for endpoint-related runtime storage."""

    def __init__(
        self,
        root: Path,
        logger: LoggerType,
        addr: Union[IpHost, tuple[str, int]],
        data_sender: TftpDataSender,
        ack_sender: TftpAckSender,
        error_sender: TftpErrorSender,
    ) -> None:
        """Initialize instance."""

        super().__init__(logger=logger)

        self._path = root

        self.addr = addr

        self.data_sender = data_sender
        self.ack_sender = ack_sender
        self.error_sender = error_sender

        # Avoid concurrency bugs when actively writing or reading.
        self.lock = asyncio.Lock()

        # Message receiving.
        self.awaiting_acks: dict[int, asyncio.Event] = {}
        self.awaiting_blocks: dict[int, asyncio.Event] = {}
        self.blocks: dict[int, bytes] = {}

        # Can be upgraded via RFC 2347.
        self.max_block_size = TFTP_MAX_BLOCK

        # Runtime settings.
        self.period: float = 0.25
        self.timeout: float = 1.0
        self.log_limiter = RateLimiter.from_s(1.0)

    def chunk_sender(self, block: int, data: bytes) -> Callable[[], None]:
        """Create a method that sends a specific block of data."""

        def sender() -> None:
            """Send a block of data."""
            self.data_sender(block, data, self.addr)

        return sender

    def _ack_sender(self, block: int) -> Callable[[], None]:
        """
        Create a method that sends an acknowledgement for a specific block
        number.
        """

        def sender() -> None:
            """Send an acknowledgement."""
            self.ack_sender(block, self.addr)

        return sender

    def set_root(self, path: Path) -> None:
        """Set a new root path for this instance."""

        self._path = path

    def handle_data(self, block: int, data: bytes) -> None:
        """Handle a data payload."""

        if block in self.awaiting_blocks:
            self.blocks[block] = data
            self.awaiting_blocks[block].set()
            del self.awaiting_blocks[block]
        else:
            self.error_sender(
                TftpErrorCode.UNKNOWN_ID,
                "Not expecting any data (got "
                f"block={block} - {len(data)} bytes)",
                self.addr,
            )

    def handle_ack(self, block: int) -> None:
        """Handle a block acknowledgement."""

        if block in self.awaiting_acks:
            self.awaiting_acks[block].set()
            del self.awaiting_acks[block]
        else:
            self.governed_log(
                self.log_limiter,
                "Not expecting any ack (got %d).",
                block,
                level=logging.ERROR,
            )

            # Sending an error seems to cause more harm than good.
            # self.error_sender(TftpErrorCode.UNKNOWN_ID, msg, self.addr)

    def __str__(self) -> str:
        """Get this instance as a string."""
        return f"{self.addr[0]}:{self.addr[1]}"

    def handle_error(self, error_code: TftpErrorCode, message: str) -> None:
        """Handle a tftp error message."""

        self.governed_log(
            self.log_limiter,
            "%s '%s' %s.",
            self,
            error_code.name,
            message,
            level=logging.ERROR,
        )

    async def ingest_file(self, stream: BinaryIO) -> bool:
        """Ingest incoming file data and write to a stream."""

        keep_going = True
        idx = 1
        curr_size = 0
        written = 0
        while keep_going:
            # Set up event trigger for expected data payload.
            event = asyncio.Event()
            self.awaiting_blocks[idx] = event

            keep_going = (
                await repeat_until(
                    # Acknowledge the previous message until we get new
                    # data.
                    self._ack_sender(idx - 1),
                    event,
                    self.period,
                    self.timeout,
                )
                and idx in self.blocks
            )

            if keep_going:
                # Write chunk.
                data = self.blocks[idx]
                curr_size = len(data)

                # If this occurs, it's probably RFC 2348 (using this assertion
                # to determine practical need for that support).
                assert curr_size <= self.max_block_size, curr_size

                stream.write(data)
                written += curr_size

                # We only expect future iterations if data payloads are
                # saturated.
                keep_going = curr_size >= self.max_block_size

            # Ensure state is cleaned up.
            self.blocks.pop(idx, None)
            self.awaiting_blocks.pop(idx, None)

            if keep_going:
                idx += 1

        # Send the final acknowledgement for a bit ("dally" per rfc).
        success = written > 0 and curr_size < self.max_block_size
        if success:
            await repeat_until(
                self._ack_sender(idx),
                asyncio.Event(),
                DALLY_PERIOD,
                DALLY_TIMEOUT,
            )

        return success

    async def _process_write_request(self, path: Path, mode: str) -> None:
        """Process a write request."""

        async with AsyncExitStack() as stack:
            # Claim write lock and ignore cancellation.
            stack.enter_context(suppress(asyncio.CancelledError))
            await stack.enter_async_context(self.lock)

            path_fd = stack.enter_context(path.open("wb"))

            with self.log_time(
                "Ingesting (%s) '%s'", mode, path, reminder=True
            ):
                success = await self.ingest_file(path_fd)

            self.logger.info(
                "%s to write (%s) '%s' from %s:%d.",
                "Succeeded" if success else "Failed",
                mode,
                FileInfo.from_file(path),
                self.addr[0],
                self.addr[1],
            )

    def handle_write_request(
        self, filename: str, mode: str
    ) -> Optional[asyncio.Task[None]]:
        """Handle a write request."""

        path = self.get_path(filename)

        # Ensure we can service this request.
        if not self._check_permission(path, "wb"):
            return None

        return asyncio.create_task(self._process_write_request(path, mode))

    async def serve_file(self, path: Path) -> bool:
        """Serve file chunks via this endpoint."""

        # Set up (outgoing) transaction.
        success = True
        idx = 1

        with self.log_time(
            "Serving '%s'", FileInfo.from_file(path), reminder=True
        ):
            for chunk in tftp_chunks(path, self.max_block_size):
                # Validate index. Remove at some point?
                assert idx not in self.awaiting_acks, idx
                assert idx < 2**16, idx

                # Prepare event trigger.
                event = asyncio.Event()
                self.awaiting_acks[idx] = event

                if not await repeat_until(
                    self.chunk_sender(idx, chunk),
                    event,
                    self.period,
                    self.timeout,
                ):
                    success = False
                    self.awaiting_acks.pop(idx, None)
                    break

                idx += 1

        return success

    async def _process_read_request(self, path: Path, mode: str) -> None:
        """
        Service a read request by sending file chunk data.
        """

        async with AsyncExitStack() as stack:
            # Claim read lock and ignore cancellation.
            stack.enter_context(suppress(asyncio.CancelledError))
            await stack.enter_async_context(self.lock)

            success = await self.serve_file(path)

            self.logger.info(
                "%s to serve (%s) '%s' to %s:%d.",
                "Succeeded" if success else "Failed",
                mode,
                FileInfo.from_file(path),
                self.addr[0],
                self.addr[1],
            )

    def get_path(self, filename: str) -> Path:
        """Get a path from a filename."""
        return self._path.joinpath(filename)

    def handle_read_request(
        self, filename: str, mode: str
    ) -> Optional[asyncio.Task[None]]:
        """Handle a read-request message."""

        path = self.get_path(filename)

        # Ensure we can service this request.
        if not self._check_exists(path) or not self._check_permission(
            path, "rb"
        ):
            return None

        return asyncio.create_task(self._process_read_request(path, mode))

    def _check_permission(self, path: Path, mode: str) -> bool:
        """
        Check if a path can be opened in the provided mode, send an error if
        not.
        """

        result = False

        try:
            with path.open(mode):
                pass
            result = True
        except PermissionError:
            self.error_sender(
                TftpErrorCode.ACCESS_VIOLATION,
                f"Can't open={mode} '{path}'",
                self.addr,
            )

        return result

    def _check_exists(self, path: Path) -> bool:
        """Check if a file exists, send an error if not."""

        result = path.is_file()

        if not result:
            self.error_sender(
                TftpErrorCode.FILE_NOT_FOUND,
                f"Path '{path}' is not a file",
                self.addr,
            )

        return result
