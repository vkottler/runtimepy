"""
A module implementing a sample peer-program interface.
"""

# built-in
import asyncio

# internal
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
                self.struct.logger.info("Sup, it's %s.", self.struct.name)
                did_write.set()
                await asyncio.sleep(poll_period_s)
            except asyncio.CancelledError:
                keep_going = False

    def pre_environment_exchange(self) -> None:
        """Perform early initialization tasks."""

        # Trigger missed telemetry.
        with self.streaming_events():
            self.struct.poll()

    async def main(self, argv: list[str]) -> None:
        """Program entry."""

        del argv

        self.struct.poll()

        # Send remote commands.
        assert self.peer is not None
        for cmd in [
            "set a.0.really_really_long_enum very_long_member_name_2",
            "set -f a.0.enum one",
        ]:
            self.peer.command(cmd)
            await self.process_command_queue()

        # Register other async tasks.
        did_write = asyncio.Event()
        self.stderr_task = asyncio.create_task(
            self.log_message_sender(0.1, did_write)
        )
        await did_write.wait()

        self.struct.poll()

        await self.wait_json({"a": 1, "b": 2, "c": 3})

    async def cleanup(self) -> None:
        """Runs when program 'running' context exits."""

        # Cancel stderr task.
        self.stderr_task.cancel()
        await self.stderr_task
