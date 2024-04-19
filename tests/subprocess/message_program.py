"""
A sample program for the subprocess manager to invoke.
"""

# built-in
import asyncio
import sys

# third-party
from vcorelib.asyncio import run_handle_interrupt

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.subprocess.program import PeerProgram


async def stderr_writer(
    poll_period_s: float, did_write: asyncio.Event
) -> None:
    """Write to stderr periodically."""

    keep_going = True
    while keep_going:
        try:
            print("Sup, it's stderr.", file=sys.stderr, flush=True)
            did_write.set()
            await asyncio.sleep(poll_period_s)
        except asyncio.CancelledError:
            keep_going = False


async def main(argv: list[str]) -> int:
    """Program entry."""

    del argv

    # Initialize channel environment.
    env = ChannelEnvironment()

    input_poller = PeerProgram.run_standard(env)

    # Register other async tasks.
    did_write = asyncio.Event()
    stderr_task = asyncio.create_task(stderr_writer(0.1, did_write))
    await did_write.wait()

    # Run program.
    await input_poller

    # Cancel stderr task.
    stderr_task.cancel()
    await stderr_task

    return 0


if __name__ == "__main__":
    sys.exit(run_handle_interrupt(main(sys.argv)) or 1)
