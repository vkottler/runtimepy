"""
A module implementing a channel registry.
"""

# built-in
from typing import Any as _Any
from typing import Optional as _Optional
from typing import Type as _Type
from typing import cast as _cast

# third-party
from vcorelib.io.types import JsonObject as _JsonObject

# internal
from runtimepy.channel import AnyChannel as _AnyChannel
from runtimepy.channel import Channel as _Channel
from runtimepy.mixins.regex import CHANNEL_PATTERN as _CHANNEL_PATTERN
from runtimepy.primitives import Primitivelike as _Primitivelike
from runtimepy.registry import Registry as _Registry
from runtimepy.registry.name import NameRegistry as _NameRegistry
from runtimepy.registry.name import RegistryKey as _RegistryKey


class ChannelNameRegistry(_NameRegistry):
    """A name registry with a name-matching pattern for channel names."""

    name_regex = _CHANNEL_PATTERN


class ChannelRegistry(_Registry[_Channel[_Any]]):
    """A runtime enumeration registry."""

    name_registry = ChannelNameRegistry

    @property
    def kind(self) -> _Type[_Channel[_Any]]:
        """Determine what kind of registry this is."""
        return _Channel

    def channel(
        self,
        name: str,
        kind: _Primitivelike,
        commandable: bool = False,
        enum: _RegistryKey = None,
    ) -> _Optional[_AnyChannel]:
        """Create a new channel."""

        data: _JsonObject = {
            "type": _cast(str, kind),
            "commandable": commandable,
        }
        if enum is not None:
            data["enum"] = enum

        return self.register_dict(name, data)
