"""
A module for creating channels at runtime.
"""

# built-in
from typing import Union as _Union
from typing import cast as _cast

# third-party
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.namespace import Namespace as _Namespace

# internal
from runtimepy.channel.environment.base import (
    BaseChannelEnvironment as _BaseChannelEnvironment,
)
from runtimepy.channel.environment.base import ChannelResult as _ChannelResult
from runtimepy.enum import RuntimeEnum as _RuntimeEnum
from runtimepy.enum.type import EnumTypelike as _EnumTypelike
from runtimepy.mapping import BoolMappingData as _BoolMappingData
from runtimepy.mapping import IntMappingData as _IntMappingData
from runtimepy.primitives import Primitivelike as _Primitivelike
from runtimepy.registry.name import RegistryKey as _RegistryKey


class CreateChannelEnvironment(_BaseChannelEnvironment):
    """An environment extension for creating channels."""

    def channel(
        self,
        name: str,
        kind: _Primitivelike,
        commandable: bool = False,
        enum: _Union[_RegistryKey, _RuntimeEnum] = None,
        namespace: _Namespace = None,
    ) -> _ChannelResult:
        """Create a new channel from the environment."""

        name = self.namespace(name=name, namespace=namespace)

        data: _JsonObject = {
            "type": _cast(str, kind),
            "commandable": commandable,
        }
        if enum is not None:
            if isinstance(enum, _RuntimeEnum):
                enum = enum.id
            data["enum"] = enum

        result = self.channels.register_dict(name, data)
        assert result is not None, f"Can't create channel '{name}'!"
        return self[name]

    def enum(
        self,
        name: str,
        kind: _EnumTypelike,
        items: _Union[_IntMappingData, _BoolMappingData] = None,
        namespace: _Namespace = None,
    ) -> _RuntimeEnum:
        """Create a new enum from the environment."""

        name = self.namespace(name=name, namespace=namespace)

        data: _JsonObject = {"type": _cast(str, kind)}
        if items is not None:
            data["items"] = items  # type: ignore

        result = self.enums.register_dict(name, data)
        assert result is not None, f"Can't create enum '{name}'!"
        return result
