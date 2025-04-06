"""
A module implementing a tftp (RFC 1350) interface.
"""

# built-in
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager, suppress
from os import fsync
from pathlib import Path
from typing import Any, AsyncIterator

# third-party
from vcorelib.asyncio.poll import repeat_until
from vcorelib.paths.context import PossiblePath, as_path, tempfile
from vcorelib.paths.hashing import file_md5_hex
from vcorelib.paths.info import FileInfo

# internal
from runtimepy.net import normalize_host
from runtimepy.net.udp.tftp.base import (
    DEFAULT_TIMEOUT_S,
    REEMIT_PERIOD_S,
    BaseTftpConnection,
    TftpErrorHandler,
)
from runtimepy.net.udp.tftp.enums import DEFAULT_MODE
from runtimepy.net.util import IpHostTuplelike


class TftpConnection(BaseTftpConnection):
    """A class implementing a basic tftp interface."""

    async def request_read(
        self,
        destination: Path,
        filename: str,
        mode: str = DEFAULT_MODE,
        addr: IpHostTuplelike = None,
    ) -> bool:
        """Request a tftp read operation."""

        end_of_data = False
        idx = 1

        async with AsyncExitStack() as stack:
            # Claim read lock and ignore cancellation.
            stack.enter_context(suppress(asyncio.CancelledError))

            endpoint, event = await self._await_first_block(stack, addr=addr)

            def ack_sender() -> None:
                """Send acks."""
                endpoint.ack_sender(idx - 1, endpoint.addr)

            def send_rrq() -> None:
                """Send request"""

                self.send_rrq(filename, mode=mode, addr=addr)
                self.logger.info(
                    "Requesting '%s' (%s) -> %s.", filename, mode, destination
                )

            with self.log_time("Awaiting first data block", reminder=True):
                # Wait for first data block.
                if not await repeat_until(
                    send_rrq,
                    event,
                    endpoint.period.value,
                    endpoint.timeout.value,
                ):
                    endpoint.awaiting_blocks.pop(idx, None)
                    self.logger.error("Didn't receive any data block.")
                    return False

            path_fd = stack.enter_context(destination.open("wb"))

            end_of_data = False

            def write_block() -> None:
                """Write block."""

                # Write block.
                nonlocal idx
                data = endpoint.blocks[idx]
                path_fd.write(data)
                del endpoint.blocks[idx]

                # Compute if this is the end of the stream.
                nonlocal end_of_data
                end_of_data = len(data) < endpoint.max_block_size
                if not end_of_data:
                    idx += 1
                else:
                    fsync(path_fd.fileno())

            write_block()

            success = True
            while not end_of_data and success:
                event = asyncio.Event()
                endpoint.awaiting_blocks[idx] = event

                success = await repeat_until(
                    ack_sender,
                    event,
                    endpoint.period.value,
                    endpoint.timeout.value,
                )
                if success:
                    write_block()

            # Repeat last ack in the background.
            if end_of_data:
                self._conn_tasks.append(
                    asyncio.create_task(
                        repeat_until(  # type: ignore
                            ack_sender,
                            asyncio.Event(),
                            endpoint.period.value,
                            endpoint.timeout.value,
                        )
                    )
                )

                # Ensure at least one ack sends.
                await asyncio.sleep(0.01)

        self.logger.info(
            "Read %s (%s).",
            FileInfo.from_file(destination),
            "end of data" if end_of_data else "not end of data",
        )

        return end_of_data

    async def request_write(
        self,
        source: PossiblePath,
        filename: str,
        mode: str = DEFAULT_MODE,
        addr: IpHostTuplelike = None,
        verify: bool = True,
    ) -> bool:
        """Request a tftp write operation."""

        result = False

        with as_path(source) as src:
            async with AsyncExitStack() as stack:
                # Claim write lock and ignore cancellation.
                stack.enter_context(suppress(asyncio.CancelledError))

                # Set up first-ack handling.
                endpoint, event = await self._await_first_ack(stack, addr=addr)

                def send_wrq() -> None:
                    """Send request."""
                    self.send_wrq(filename, mode=mode, addr=addr)

                # Wait for zeroeth ack.
                with self.log_time("Awaiting first ack", reminder=True):
                    if not await repeat_until(
                        send_wrq,
                        event,
                        endpoint.period.value,
                        endpoint.timeout.value,
                    ):
                        endpoint.awaiting_acks.pop(0, None)
                        return result

                result = await endpoint.serve_file(src)

            # Verify by reading back.
            if verify and result:
                with self.log_time("Verifying write via read", reminder=True):
                    with tempfile() as tmp:
                        result = await self.request_read(
                            tmp, filename, mode=mode, addr=addr
                        )

                        # Compare hashes.
                        self.logger.info(
                            "Reading '%s' %s.",
                            filename,
                            "succeeded" if result else "failed",
                        )
                        if result:
                            result = file_md5_hex(src) == file_md5_hex(tmp)
                            self.logger.info(
                                "MD5 sums %s",
                                "matched." if result else "didn't match!",
                            )

        return result


TFTP_PORT = 69


@asynccontextmanager
async def tftp(
    addr: IpHostTuplelike,
    process_kwargs: dict[str, Any] = None,
    connection_kwargs: dict[str, Any] = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    reemit_period_s: float = REEMIT_PERIOD_S,
    error_handler: TftpErrorHandler = None,
) -> AsyncIterator[TftpConnection]:
    """Use a tftp connection as a managed context."""

    if process_kwargs is None:
        process_kwargs = {}
    if connection_kwargs is None:
        connection_kwargs = {}

    addr = normalize_host(*addr)

    # Create and start connection.
    conn = await TftpConnection.create_connection(
        remote_addr=(addr.name, addr.port), **connection_kwargs
    )

    # Add error handlers.
    if error_handler is not None:
        conn.error_handlers.append(error_handler)

    async with conn.process_then_disable(**process_kwargs):
        # Set parameters.
        conn.endpoint_timeout.value = timeout_s
        conn.endpoint_period.value = reemit_period_s
        yield conn


async def tftp_write(
    addr: IpHostTuplelike,
    source: PossiblePath,
    filename: str,
    mode: str = DEFAULT_MODE,
    verify: bool = True,
    process_kwargs: dict[str, Any] = None,
    connection_kwargs: dict[str, Any] = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    reemit_period_s: float = REEMIT_PERIOD_S,
    error_handler: TftpErrorHandler = None,
) -> bool:
    """Attempt to perform a tftp write."""

    async with tftp(
        addr,
        process_kwargs=process_kwargs,
        connection_kwargs=connection_kwargs,
        timeout_s=timeout_s,
        reemit_period_s=reemit_period_s,
        error_handler=error_handler,
    ) as conn:
        # Perform tftp interaction.
        result = await conn.request_write(
            source, filename, mode=mode, addr=addr, verify=verify
        )

    return result


async def tftp_read(
    addr: IpHostTuplelike,
    destination: Path,
    filename: str,
    mode: str = DEFAULT_MODE,
    process_kwargs: dict[str, Any] = None,
    connection_kwargs: dict[str, Any] = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    reemit_period_s: float = REEMIT_PERIOD_S,
    error_handler: TftpErrorHandler = None,
) -> bool:
    """Attempt to perform a tftp read."""

    async with tftp(
        addr,
        process_kwargs=process_kwargs,
        connection_kwargs=connection_kwargs,
        timeout_s=timeout_s,
        reemit_period_s=reemit_period_s,
        error_handler=error_handler,
    ) as conn:
        result = await conn.request_read(
            destination, filename, mode=mode, addr=addr
        )

    return result
