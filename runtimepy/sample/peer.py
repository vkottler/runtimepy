"""
A sample peer program interface.
"""

# built-in
import asyncio

# internal
from runtimepy.subprocess.peer import RuntimepyPeer


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
