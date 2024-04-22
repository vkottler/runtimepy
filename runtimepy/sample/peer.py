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

        # Send remote commands.
        assert self.peer is not None
        for cmd in [
            "set a.0.really_really_long_enum very_long_member_name_3",
            "set a.0.enum three",
            "set -f a.0.enum three",
            "set a.0.really_really_long_enum very_long_member_name_2",
        ]:
            self.peer.command(cmd)
            await self.process_command_queue()

        self.struct.poll()

        self.stage_remote_log("What's good %s.", "bud")

        await self.wait_json({"a": 1, "b": 2, "c": 3})

        await asyncio.sleep(0)

        self.struct.poll()
