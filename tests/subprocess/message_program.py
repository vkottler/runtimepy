"""
A sample program for the subprocess manager to invoke.
"""

# built-in
import asyncio
import sys

# third-party
from vcorelib.asyncio import run_handle_interrupt

# internal
from runtimepy.net.arbiter.struct import SampleStruct
from runtimepy.subprocess.program import PeerProgram


async def log_message_sender(
    struct: SampleStruct, poll_period_s: float, did_write: asyncio.Event
) -> None:
    """Write to stderr periodically."""

    keep_going = True
    while keep_going:
        try:
            struct.logger.info("Sup, it's %s.", "a log sending task")
            did_write.set()
            await asyncio.sleep(poll_period_s)
        except asyncio.CancelledError:
            keep_going = False


async def main(argv: list[str]) -> int:
    """Program entry."""

    del argv

    # Initialize channel environment.
    struct = SampleStruct("test", {})

    async with PeerProgram.running(struct) as (task, peer):
        # Register other async tasks.
        did_write = asyncio.Event()
        stderr_task = asyncio.create_task(
            log_message_sender(struct, 0.1, did_write)
        )
        await did_write.wait()

        peer.struct.poll()

        # Generate event telemetry.
        with peer.streaming_events():
            peer.struct.poll()

        # Run program.
        await task

        # Cancel stderr task.
        stderr_task.cancel()
        await stderr_task

    return 0


if __name__ == "__main__":
    sys.exit(run_handle_interrupt(main(sys.argv)) or 1)
