"""
A module implementing a channel environment.
"""

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


class ChannelEnvironment(
    _ArrayChannelEnvironment,
    _FileChannelEnvironment,
    _CreateChannelEnvironment,
):
    """A class integrating channel and enumeration registries."""
