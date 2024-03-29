"""
A module for working with test data.
"""

# built-in
import asyncio
from os.path import join
from pathlib import Path
from sys import version_info
from typing import List, Tuple

# third-party
import pkg_resources
from vcorelib.platform import is_windows

# internal
from runtimepy import PKG_NAME
from runtimepy.net.arbiter import ArbiterTask
from runtimepy.net.connection import Connection
from runtimepy.net.tcp.connection import TcpConnection
from runtimepy.net.udp.connection import UdpConnection
from runtimepy.net.websocket.connection import WebsocketConnection
from runtimepy.task import PeriodicTask


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

    def init(self) -> None:
        """Initialize this instance."""

        self.message_rx = asyncio.Semaphore(0)

    async def process_text(self, data: str) -> bool:
        """Process a text frame."""

        stop_found = False
        for item in data.split():
            if item:
                self.logger.info("'%s'", item)
                stop_found = "stop" in item
                if stop_found:
                    break

        # Signal that we've received a message.
        self.message_rx.release()

        return not stop_found

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""
        return await self.process_text(data.decode())


class SampleUdpConnection(UdpConnection, SampleConnectionMixin):
    """A sample connection class."""

    async def process_datagram(
        self, data: bytes, addr: Tuple[str, int]
    ) -> bool:
        """Process a datagram."""
        return await self.process_binary(data)


class SampleTcpConnection(TcpConnection, SampleConnectionMixin):
    """A sample connection class."""


class SampleWebsocketConnection(WebsocketConnection, SampleConnectionMixin):
    """A sample connection class."""


async def release_after(sig: asyncio.Event, time: float) -> None:
    """Disable a connection after a delay."""
    await asyncio.sleep(time)
    sig.set()


class SampleTask(PeriodicTask):
    """A sample task."""

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

        self.logger.info("Iteration.")

        return True


class OverrunTask(PeriodicTask):
    """A sample task."""

    async def dispatch(self) -> bool:
        """Dispatch an iteration of this task."""

        await asyncio.sleep(self.period_s.value * 2)
        return True


class SampleArbiterTask(ArbiterTask, SampleTask):
    """A sample arbiter task."""


def can_use_uvloop() -> bool:
    """Determine if tests should try to use uvloop."""

    return not is_windows() and (
        version_info.major >= 3 and version_info.minor >= 11
    )


def base_args(command: str) -> List[str]:
    """Get base command-line arguments."""

    base = [PKG_NAME]

    # Don't use uvloop if not using Python 3.11.
    if not can_use_uvloop() and not is_windows():
        base.append("--no-uvloop")

    base.append(command)
    return base
