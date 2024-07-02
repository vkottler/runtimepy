"""
A module implementing a tftp (RFC 1350) interface.
"""

# built-in
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager, suppress
from os import fsync
from pathlib import Path
from typing import Any, AsyncIterator, Union

# third-party
from vcorelib.asyncio.poll import repeat_until
from vcorelib.paths.context import tempfile
from vcorelib.paths.hashing import file_md5_hex
from vcorelib.paths.info import FileInfo

# internal
from runtimepy.net import IpHost, normalize_host
from runtimepy.net.udp.tftp.base import BaseTftpConnection
from runtimepy.net.udp.tftp.enums import DEFAULT_MODE
from runtimepy.util import PossiblePath, as_path


class TftpConnection(BaseTftpConnection):
    """A class implementing a basic tftp interface."""

    async def request_read(
        self,
        destination: Path,
        filename: str,
        mode: str = DEFAULT_MODE,
        addr: Union[IpHost, tuple[str, int]] = None,
    ) -> bool:
        """Request a tftp read operation."""

        endpoint = self.endpoint(addr)
        end_of_data = False
        idx = 1

        def ack_sender() -> None:
            """Send acks."""
            nonlocal idx
            self.send_ack(block=idx - 1, addr=addr)

        async with AsyncExitStack() as stack:
            # Claim read lock and ignore cancellation.
            stack.enter_context(suppress(asyncio.CancelledError))
            await stack.enter_async_context(endpoint.lock)

            def send_rrq() -> None:
                """Send request"""

                self.send_rrq(filename, mode=mode, addr=addr)
                self.logger.info(
                    "Requesting '%s' (%s) -> %s.", filename, mode, destination
                )

            event = asyncio.Event()
            endpoint.awaiting_blocks[idx] = event

            with self.log_time("Awaiting first data block", reminder=True):
                # Wait for first data block.
                if not await repeat_until(
                    send_rrq, event, endpoint.period, endpoint.timeout
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
                    ack_sender, event, endpoint.period, endpoint.timeout
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
                        endpoint.period,
                        endpoint.timeout,
                    )
                )
            )

        # Make a to-string or log method for vcorelib FileInfo?
        #
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
        addr: Union[IpHost, tuple[str, int]] = None,
        verify: bool = True,
    ) -> bool:
        """Request a tftp write operation."""

        result = False
        endpoint = self.endpoint(addr)

        with as_path(source) as src:
            async with AsyncExitStack() as stack:
                # Claim write lock and ignore cancellation.
                stack.enter_context(suppress(asyncio.CancelledError))
                await stack.enter_async_context(endpoint.lock)

                event = asyncio.Event()
                endpoint.awaiting_acks[0] = event

                def send_wrq() -> None:
                    """Send request."""
                    self.send_wrq(filename, mode=mode, addr=addr)

                # Wait for zeroeth ack.
                with self.log_time("Awaiting first ack", reminder=True):
                    if not await repeat_until(
                        send_wrq, event, endpoint.period, endpoint.timeout
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
                        if result:
                            result = file_md5_hex(src) == file_md5_hex(tmp)
                            self.logger.info(
                                "MD5 sums %s",
                                "matched." if result else "didn't match!",
                            )

        return result


@asynccontextmanager
async def tftp(
    addr: Union[IpHost, tuple[str, int]],
    process_kwargs: dict[str, Any] = None,
    connection_kwargs: dict[str, Any] = None,
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
    async with conn.process_then_disable(**process_kwargs):
        yield conn


async def tftp_write(
    addr: Union[IpHost, tuple[str, int]],
    source: PossiblePath,
    filename: str,
    mode: str = DEFAULT_MODE,
    verify: bool = True,
    process_kwargs: dict[str, Any] = None,
    connection_kwargs: dict[str, Any] = None,
) -> bool:
    """Attempt to perform a tftp write."""

    async with tftp(
        addr,
        process_kwargs=process_kwargs,
        connection_kwargs=connection_kwargs,
    ) as conn:

        # Perform tftp interaction.
        result = await conn.request_write(
            source, filename, mode=mode, addr=addr, verify=verify
        )

    return result


async def tftp_read(
    addr: Union[IpHost, tuple[str, int]],
    destination: Path,
    filename: str,
    mode: str = DEFAULT_MODE,
    process_kwargs: dict[str, Any] = None,
    connection_kwargs: dict[str, Any] = None,
) -> bool:
    """Attempt to perform a tftp read."""

    async with tftp(
        addr,
        process_kwargs=process_kwargs,
        connection_kwargs=connection_kwargs,
    ) as conn:

        result = await conn.request_read(
            destination, filename, mode=mode, addr=addr
        )

    return result
