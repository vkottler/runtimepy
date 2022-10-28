"""
A module implementing a channel registry.
"""

# built-in
from re import compile as _compile
from typing import Any as _Any
from typing import Type as _Type

# internal
from runtimepy.channel import Channel as _Channel
from runtimepy.registry import Registry as _Registry
from runtimepy.registry.name import NameRegistry as _NameRegistry

# test


class ChannelNameRegistry(_NameRegistry):
    """A name registry with a name-matching pattern for channel names."""

    name_regex = _compile("^[a-z0-9_.]+$")


class ChannelRegistry(_Registry[_Channel[_Any]]):
    """A runtime enumeration registry."""

    name_registry = ChannelNameRegistry

    @property
    def kind(self) -> _Type[_Channel[_Any]]:
        """Determine what kind of registry this is."""
        return _Channel
