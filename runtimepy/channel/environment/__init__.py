"""
A module implementing a channel environment.
"""

# built-in
from typing import Iterator as _Iterator

# internal
from runtimepy.channel.environment.array import (
    ArrayChannelEnvironment as _ArrayChannelEnvironment,
)
from runtimepy.channel.environment.create import (
    CreateChannelEnvironment as _CreateChannelEnvironment,
)
from runtimepy.channel.environment.file import (
    FileChannelEnvironment as _FileChannelEnvironment,
)
from runtimepy.channel.registry import ParsedEvent


class ChannelEnvironment(
    _ArrayChannelEnvironment,
    _FileChannelEnvironment,
    _CreateChannelEnvironment,
):
    """A class integrating channel and enumeration registries."""

    def ingest(self, point: ParsedEvent) -> None:
        """
        Update internal state based on an event. Note that the event timestamp
        is not respected.
        """
        self.set(point.name, point.value)

    @property
    def names(self) -> _Iterator[str]:
        """Iterate over registered names in the environment."""
        yield from self.channels.names.names
