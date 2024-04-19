"""
A sample program for the subprocess manager to invoke.
"""

# built-in
import sys

# third-party
from vcorelib.asyncio import run_handle_interrupt

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.subprocess.program import PeerProgram


async def main(argv: list[str]) -> int:
    """Program entry."""

    del argv

    print("Sup, it's stderr.", file=sys.stderr, flush=True)

    # Initialize channel environment.
    env = ChannelEnvironment()

    # Run program.
    await PeerProgram.run_standard(env)

    return 0


if __name__ == "__main__":
    sys.exit(run_handle_interrupt(main(sys.argv)) or 1)
