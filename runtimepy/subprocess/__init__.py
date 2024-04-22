"""
A module implementing a subprocess management interface.
"""

# built-in
from asyncio import Queue, get_running_loop, wait_for
from contextlib import asynccontextmanager, suppress
from logging import getLogger
from typing import AsyncIterator

# third-party
from vcorelib.asyncio.subprocess import log_process_info
from vcorelib.logging import LoggerType
from vcorelib.math import nano_str
from vcorelib.platform import reconcile_platform

# internal
from runtimepy.subprocess.protocol import RuntimepySubprocessProtocol

POLL_RATE = 2.0
LOG = getLogger(__name__)


async def shutdown_protocol(
    protocol: RuntimepySubprocessProtocol,
    poll_rate: float = 2.0,
    logger: LoggerType = LOG,
) -> None:
    """Shutdown a subprocess protocol instance."""

    if protocol.stdin.can_write_eof():
        logger.debug("Writing EOF to %d.", protocol.pid)
        protocol.stdin.write_eof()

    while not protocol.exited.is_set():
        with suppress(TimeoutError):
            await wait_for(protocol.exited.wait(), poll_rate)

        # Close transport.
        logger.debug("Closing transport for %d.", protocol.pid)
        protocol.transport.close()


async def close_protocol(
    protocol: RuntimepySubprocessProtocol,
    poll_rate: float = 2.0,
    stdout: Queue[bytes] = None,
    stderr: Queue[bytes] = None,
    logger: LoggerType = LOG,
) -> None:
    """Shutdown a protocol instance."""

    # Handle shutting down the process.
    if not protocol.exited.is_set():
        await shutdown_protocol(protocol, poll_rate=poll_rate, logger=logger)
    assert protocol.exited.is_set()

    # Log exit status.
    logger.info(
        "%d exited %d in %ss.",
        protocol.pid,
        protocol.transport.get_returncode(),
        nano_str(protocol.elapsed_time, is_time=True),
    )

    # Log pending data remaining on stdout queue.
    if stdout is not None and not stdout.empty():
        count = 0
        while not stdout.empty():
            message = stdout.get_nowait()
            if message:
                logger.warning("stdout message: %s", message)
            count += len(message)

        if count:
            logger.warning("stdout had %d remaining bytes.", count)

    # Log pending data remaining on stderr queue.
    if stderr is not None and not stderr.empty():
        count = 0
        while not stderr.empty():
            message = stderr.get_nowait()
            if message:
                logger.warning("stderr message: %s", message)
            count += len(message)

        if count:
            logger.warning("stdout had %d remaining bytes.", count)


@asynccontextmanager
async def spawn_exec(
    *args: str,
    stdout: Queue[bytes] = None,
    stderr: Queue[bytes] = None,
    logger: LoggerType = LOG,
    **kwargs,
) -> AsyncIterator[RuntimepySubprocessProtocol]:
    """Create a subprocess."""

    program, list_args = reconcile_platform(args[0], args[1:])

    _, protocol = await get_running_loop().subprocess_exec(
        RuntimepySubprocessProtocol, program, *list_args, **kwargs
    )

    rel = log_process_info(program, *list_args)
    logger.info("Started exec '%s %s' %d.", rel[0], rel[1], protocol.pid)

    protocol.stdout_queue = stdout
    protocol.stderr_queue = stderr

    try:
        yield protocol
    finally:
        await close_protocol(
            protocol, stdout=stdout, stderr=stderr, logger=logger
        )


@asynccontextmanager
async def spawn_shell(
    cmd: str,
    stdout: Queue[bytes] = None,
    stderr: Queue[bytes] = None,
    logger: LoggerType = LOG,
    **kwargs,
) -> AsyncIterator[RuntimepySubprocessProtocol]:
    """Create a shell subprocess."""

    _, protocol = await get_running_loop().subprocess_shell(
        RuntimepySubprocessProtocol, cmd, **kwargs
    )

    logger.info("Started shell '%s' %d.", cmd, protocol.pid)

    protocol.stdout_queue = stdout
    protocol.stderr_queue = stderr

    try:
        yield protocol
    finally:
        await close_protocol(
            protocol, stdout=stdout, stderr=stderr, logger=logger
        )
