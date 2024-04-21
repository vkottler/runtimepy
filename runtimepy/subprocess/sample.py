"""
A sample peer program interface.
"""

# built-in
import asyncio

# internal
from runtimepy.subprocess.peer import RuntimepyPeer
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
                self.struct.logger.info("Sup, it's %s.", "a log sending task")
                did_write.set()
                await asyncio.sleep(poll_period_s)
            except asyncio.CancelledError:
                keep_going = False

    async def main(self, argv: list[str]) -> None:
        """Program entry."""

        del argv

        with self.streaming_events():
            self.struct.poll()

        # Register other async tasks.
        did_write = asyncio.Event()
        self.stderr_task = asyncio.create_task(
            self.log_message_sender(0.1, did_write)
        )
        await did_write.wait()

        self.struct.poll()

        await self.wait_json({"a": 1, "b": 2, "c": 3})

        # Generate event telemetry.
        with self.streaming_events():
            self.struct.poll()

    async def cleanup(self) -> None:
        """Runs when program 'running' context exits."""

        # Cancel stderr task.
        self.stderr_task.cancel()
        await self.stderr_task


class SamplePeer(RuntimepyPeer):
    """A sample peer program."""

    async def main(self) -> None:
        """Program entry."""

        self.struct.poll()

        self.stage_remote_log("What's good %s.", "bud")

        await self.wait_json({"a": 1, "b": 2, "c": 3})

        await asyncio.sleep(0)

        self.struct.poll()

        for name, events in self.poll_telemetry().items():
            self.logger.info("'%s' %d events parsed.", name, len(events))
