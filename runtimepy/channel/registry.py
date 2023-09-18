"""
A module implementing a channel registry.
"""

# built-in
from typing import Any as _Any
from typing import Optional as _Optional
from typing import Type as _Type
from typing import Union

# third-party
from vcorelib.io.types import JsonObject as _JsonObject

# internal
from runtimepy.channel import AnyChannel as _AnyChannel
from runtimepy.channel import Channel as _Channel
from runtimepy.mixins.regex import CHANNEL_PATTERN as _CHANNEL_PATTERN
from runtimepy.primitives import ChannelScaling, Primitive
from runtimepy.primitives import Primitivelike as _Primitivelike
from runtimepy.primitives import normalize
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
        kind: Union[Primitive[_Any], _Primitivelike],
        commandable: bool = False,
        enum: _RegistryKey = None,
        scaling: ChannelScaling = None,
    ) -> _Optional[_AnyChannel]:
        """Create a new channel."""

        if isinstance(kind, str):
            kind = normalize(kind)

        if isinstance(kind, Primitive):
            primitive = kind
        else:
            primitive = kind()

        if scaling:
            assert not primitive.scaling or scaling == primitive.scaling, (
                scaling,
                primitive.scaling,
            )
            primitive.scaling = scaling

        data: _JsonObject = {
            "type": str(primitive.kind),
            "commandable": commandable,
        }
        if enum is not None:
            data["enum"] = enum

        result = self.register_dict(name, data)

        # Replace the underlying primitive, in case it was direclty passed in.
        if result is not None:
            result.raw = primitive

        return result
