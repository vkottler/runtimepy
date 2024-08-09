"""
A module implementing a channel environment.
"""

# built-in
from typing import Iterator as _Iterator

# internal
from runtimepy.channel import Default as _Default
from runtimepy.channel.environment.array import (
    ArrayChannelEnvironment as _ArrayChannelEnvironment,
)
from runtimepy.channel.environment.create import (
    CreateChannelEnvironment as _CreateChannelEnvironment,
)
from runtimepy.channel.environment.file import (
    FileChannelEnvironment as _FileChannelEnvironment,
)
from runtimepy.channel.environment.telemetry import (
    TelemetryChannelEnvironment as _TelemetryChannelEnvironment,
)


class ChannelEnvironment(
    _TelemetryChannelEnvironment,
    _ArrayChannelEnvironment,
    _FileChannelEnvironment,
    _CreateChannelEnvironment,
):
    """A class integrating channel and enumeration registries."""

    def search_names(
        self, pattern: str, exact: bool = False
    ) -> _Iterator[str]:
        """Search for names belonging to this environment."""
        yield from self.channels.names.search(pattern, exact=exact)

    def set_default(self, key: str, default: _Default) -> None:
        """Set a new default value for a channel."""

        chan, _ = self[key]
        chan.default = default

    @property
    def num_defaults(self) -> int:
        """
        Determine the number of channels in this environment configured with
        a default value.
        """

        result = 0

        for name in self.names:
            chan = self.get(name)
            if chan is not None and chan[0].has_default:
                result += 1

        return result
