"""
A module for working with test data.
"""

# built-in
import asyncio
from os.path import join
from pathlib import Path

# third-party
import pkg_resources

# internal
from runtimepy.net.connection import Connection


def resource(
    resource_name: str, *parts: str, valid: bool = True, pkg: str = __name__
) -> Path:
    """Locate the path to a test resource."""

    return Path(
        pkg_resources.resource_filename(
            pkg,
            join(
                "data", "valid" if valid else "invalid", resource_name, *parts
            ),
        )
    )


class SampleConnectionMixin(Connection):
    """A sample connection class."""

    async def process_text(self, data: str) -> bool:
        """Process a text frame."""

        stop_found = False
        for item in data.split():
            self.logger.info("'%s'", item)
            stop_found = "stop" in item
            if stop_found:
                break

        return not stop_found

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""
        return await self.process_text(data.decode())


async def release_after(sig: asyncio.Event, time: float) -> None:
    """Disable a connection after a delay."""
    await asyncio.sleep(time)
    sig.set()
