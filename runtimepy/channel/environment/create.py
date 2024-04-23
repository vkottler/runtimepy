"""
A module for creating channels at runtime.
"""

# built-in
from typing import Any as _Any
from typing import Union as _Union
from typing import cast as _cast

# third-party
from vcorelib.namespace import Namespace as _Namespace

# internal
from runtimepy.channel import FloatChannel as _FloatChannel
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
from runtimepy.enum.registry import DEFAULT_ENUM_PRIMITIVE
from runtimepy.enum.types import EnumTypelike as _EnumTypelike
from runtimepy.mapping import EnumMappingData as _EnumMappingData
from runtimepy.primitives import ChannelScaling, Primitive
from runtimepy.primitives import Primitivelike as _Primitivelike
from runtimepy.registry.name import RegistryKey as _RegistryKey


class CreateChannelEnvironment(_BaseChannelEnvironment):
    """An environment extension for creating channels."""

    def channel(
        self,
        name: str,
        kind: _Union[Primitive[_Any], _Primitivelike],
        commandable: bool = False,
        enum: _Union[_RegistryKey, _RuntimeEnum] = None,
        namespace: _Namespace = None,
        scaling: ChannelScaling = None,
        min_period_s: float = None,
        **kwargs,
    ) -> _ChannelResult:
        """Create a new channel from the environment."""

        assert not self.finalized, "Environment already finalized!"

        # Apply the current (or provided) namespace.
        name = self.namespace(name=name, namespace=namespace)

        if enum is not None:
            if isinstance(enum, _RuntimeEnum):
                enum = enum.id

        # Register the channel.
        result = self.channels.channel(
            name,
            kind,
            commandable=commandable,
            enum=enum,
            scaling=scaling,
            **kwargs,
        )

        assert result is not None, f"Can't create channel '{name}'!"

        # Set a minimum period if one was specified.
        if min_period_s is not None:
            result.event.set_min_period(min_period_s)

        # Keep track of any new enum channels.
        if enum is not None:
            self.channel_enums[result] = self.enums[enum]

        return self[name]

    def int_channel(
        self,
        name: str,
        kind: _Union[Primitive[_Any], _Primitivelike] = "uint32",
        commandable: bool = False,
        enum: _Union[_RegistryKey, _RuntimeEnum] = None,
        namespace: _Namespace = None,
        scaling: ChannelScaling = None,
        **kwargs,
    ) -> _IntChannelResult:
        """Create an integer channel."""

        result = _cast(
            _IntChannelResult,
            self.channel(
                name,
                kind,
                commandable=commandable,
                enum=enum,
                namespace=namespace,
                scaling=scaling,
                **kwargs,
            ),
        )

        assert result[0].raw.kind.is_integer
        self.ints.add(result[0])

        return result

    def bool_channel(
        self,
        name: str,
        kind: _Union[Primitive[_Any], _Primitivelike] = "bool",
        commandable: bool = False,
        enum: _Union[_RegistryKey, _RuntimeEnum] = None,
        namespace: _Namespace = None,
        **kwargs,
    ) -> _BoolChannelResult:
        """Create a boolean channel."""

        result = _cast(
            _BoolChannelResult,
            self.channel(
                name,
                kind,
                commandable=commandable,
                enum=enum,
                namespace=namespace,
                **kwargs,
            ),
        )

        assert result[0].raw.kind.is_boolean
        self.bools.add(result[0])

        return result

    def float_channel(
        self,
        name: str,
        kind: _Union[Primitive[_Any], _Primitivelike] = "float",
        commandable: bool = False,
        namespace: _Namespace = None,
        scaling: ChannelScaling = None,
        **kwargs,
    ) -> _FloatChannel:
        """Create a floating-point channel."""

        result = _cast(
            _FloatChannel,
            self.channel(
                name,
                kind,
                commandable=commandable,
                namespace=namespace,
                scaling=scaling,
                **kwargs,
            )[0],
        )

        assert result.raw.kind.is_float
        self.floats.add(result)

        return result

    def enum(
        self,
        name: str,
        kind: _EnumTypelike,
        items: _EnumMappingData = None,
        namespace: _Namespace = None,
        primitive: str = DEFAULT_ENUM_PRIMITIVE,
    ) -> _RuntimeEnum:
        """Create a new enum from the environment."""

        result = self.enums.enum(
            self.namespace(name=name, namespace=namespace),
            kind=kind,
            items=items,
            primitive=primitive,
        )
        assert result is not None, f"Can't create enum '{name}'!"
        return result
