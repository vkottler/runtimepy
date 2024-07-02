"""
A module implementing a sample peer-program interface.
"""

# built-in
import asyncio

# third-party
from vcorelib.math import RateLimiter

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.subprocess.program import PeerProgram


class SampleProgram(PeerProgram):
    """A sample peer program."""

    stderr_task: asyncio.Task[None]

    async def log_message_sender(
        self, poll_period_s: float, did_write: asyncio.Event
    ) -> None:
        """Write to stderr periodically."""

        keep_going = True
        while keep_going:
            try:
                self.struct.governed_log(
                    self.log_limiter, "Sup, it's %s.", self.struct.name
                )
                did_write.set()
                await asyncio.sleep(poll_period_s)
            except asyncio.CancelledError:
                keep_going = False

    def struct_pre_finalize(self) -> None:
        """Configure struct before finalization."""

        super().struct_pre_finalize()
        self.log_limiter = RateLimiter.from_s(2.0)

    def pre_environment_exchange(self) -> None:
        """Perform early initialization tasks."""

        # Trigger missed telemetry.
        with self.streaming_events():
            self.struct.poll()

    async def cleanup(self) -> None:
        """Runs when program 'running' context exits."""

        # Cancel stderr task.
        if hasattr(self, "stderr_task"):
            self.stderr_task.cancel()
            await self.stderr_task


async def run(app: AppInfo) -> int:
    """A network application that doesn't do anything."""

    await app.all_finalized()

    prog = SampleProgram.singleton()

    await prog.share_config({"config": app.original_config()})

    assert prog is not None

    prog.struct.poll()

    # Send remote commands.
    assert prog.peer is not None
    for cmd in [
        "set a.0.really_really_long_enum very_long_member_name_2",
        "set -f a.0.enum one",
    ]:
        prog.peer.command(cmd)
        await prog.process_command_queue()

    # Register other async tasks.
    did_write = asyncio.Event()
    prog.stderr_task = asyncio.create_task(
        prog.log_message_sender(0.1, did_write)
    )
    await did_write.wait()

    prog.struct.poll()

    await prog.wait_json({"a": 1, "b": 2, "c": 3})

    return 0
