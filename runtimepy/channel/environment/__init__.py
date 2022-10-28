"""
A module implementing a channel environment.
"""

# internal
from runtimepy.channel.environment.file import (
    FileChannelEnvironment as _FileChannelEnvironment,
)


class ChannelEnvironment(_FileChannelEnvironment):
    """A class integrating channel and enumeration registries."""
