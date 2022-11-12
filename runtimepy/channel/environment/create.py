"""
A module for creating channels at runtime.
"""

# built-in
from typing import Union as _Union
from typing import cast as _cast

# third-party
from vcorelib.namespace import Namespace as _Namespace

from runtimepy.channel import FloatChannel as _FloatChannel

# internal
from runtimepy.channel.environment.base import (
    BaseChannelEnvironment as _BaseChannelEnvironment,
)
from runtimepy.channel.environment.base import (
    BoolChannelResult as _BoolChannelResult,
)
from runtimepy.channel.environment.base import (
    IntChannelResult as _IntChannelResult,
)
from runtimepy.channel.environment.base import ChannelResult as _ChannelResult
from runtimepy.enum import RuntimeEnum as _RuntimeEnum
from runtimepy.enum.type import EnumTypelike as _EnumTypelike
from runtimepy.mapping import EnumMappingData as _EnumMappingData
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

        # Apply the current (or provided) namespace.
        name = self.namespace(name=name, namespace=namespace)

        if enum is not None:
            if isinstance(enum, _RuntimeEnum):
                enum = enum.id

        # Register the channel.
        result = self.channels.channel(
            name, kind, commandable=commandable, enum=enum
        )
        assert result is not None, f"Can't create channel '{name}'!"
        return self[name]

    def int_channel(
        self,
        name: str,
        kind: _Primitivelike = "uint32",
        commandable: bool = False,
        enum: _Union[_RegistryKey, _RuntimeEnum] = None,
        namespace: _Namespace = None,
    ) -> _IntChannelResult:
        """Create an integer channel."""

        result = self.channel(
            name, kind, commandable=commandable, enum=enum, namespace=namespace
        )
        assert result[0].raw.kind.is_integer
        return _cast(_IntChannelResult, result)

    def bool_channel(
        self,
        name: str,
        kind: _Primitivelike = "bool",
        commandable: bool = False,
        enum: _Union[_RegistryKey, _RuntimeEnum] = None,
        namespace: _Namespace = None,
    ) -> _BoolChannelResult:
        """Create a boolean channel."""

        result = self.channel(
            name, kind, commandable=commandable, enum=enum, namespace=namespace
        )
        assert result[0].raw.kind.is_boolean
        return _cast(_BoolChannelResult, result)

    def float_channel(
        self,
        name: str,
        kind: _Primitivelike = "float",
        commandable: bool = False,
        namespace: _Namespace = None,
    ) -> _FloatChannel:
        """Create a floating-point channel."""

        result = self.channel(
            name, kind, commandable=commandable, namespace=namespace
        )[0]
        assert result.raw.kind.is_float
        return _cast(_FloatChannel, result)

    def enum(
        self,
        name: str,
        kind: _EnumTypelike,
        items: _EnumMappingData = None,
        namespace: _Namespace = None,
    ) -> _RuntimeEnum:
        """Create a new enum from the environment."""

        result = self.enums.enum(
            self.namespace(name=name, namespace=namespace),
            kind=kind,
            items=items,
        )
        assert result is not None, f"Can't create enum '{name}'!"
        return result
