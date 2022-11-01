"""
A module implementing a channel environment.
"""

from runtimepy.channel.environment.create import (
    CreateChannelEnvironment as _CreateChannelEnvironment,
)

# internal
from runtimepy.channel.environment.file import (
    FileChannelEnvironment as _FileChannelEnvironment,
)


class ChannelEnvironment(_FileChannelEnvironment, _CreateChannelEnvironment):
    """A class integrating channel and enumeration registries."""
