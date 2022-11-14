"""
A channel-environment extension for working with channel names.
"""

# built-in
from typing import Iterator as _Iterator

# internal
from runtimepy.channel.environment.base import (
    BaseChannelEnvironment as _BaseChannelEnvironment,
)


class ChannelNameEnvironment(_BaseChannelEnvironment):
    """An environment extension for working with channel names."""

    @property
    def names(self) -> _Iterator[str]:
        """Iterate over registered names in the environment."""
        yield from self.channels.names.names
