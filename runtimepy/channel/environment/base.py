"""
A module implementing a base channel environment.
"""

# built-in
from typing import Dict as _Dict
from typing import Iterable as _Iterable
from typing import Optional as _Optional
from typing import Set as _Set
from typing import Tuple as _Tuple
from typing import Union as _Union
from typing import cast as _cast

# third-party
from vcorelib.namespace import NamespaceMixin as _NamespaceMixin

# internal
from runtimepy.channel import AnyChannel as _AnyChannel
from runtimepy.channel import BoolChannel as _BoolChannel
from runtimepy.channel import FloatChannel as _FloatChannel
from runtimepy.channel import IntChannel as _IntChannel
from runtimepy.channel.registry import ChannelRegistry as _ChannelRegistry
from runtimepy.enum import RuntimeEnum as _RuntimeEnum
from runtimepy.enum.registry import EnumRegistry as _EnumRegistry
from runtimepy.primitives.field import BitField as _BitField
from runtimepy.primitives.field.fields import BitFields as _BitFields
from runtimepy.primitives.field.manager import (
    BitFieldsManager as _BitFieldsManager,
)
from runtimepy.registry.name import RegistryKey as _RegistryKey

ChannelValue = _Union[bool, int, float, str]
ValueMap = _Dict[_RegistryKey, ChannelValue]

ChannelResult = _Tuple[_AnyChannel, _Optional[_RuntimeEnum]]
BitfieldResult = _Tuple[_BitField, _Optional[_RuntimeEnum]]
BoolChannelResult = _Tuple[_BoolChannel, _Optional[_RuntimeEnum]]
IntChannelResult = _Tuple[_IntChannel, _Optional[_RuntimeEnum]]


class BaseChannelEnvironment(_NamespaceMixin):
    """A class integrating channel and enumeration registries."""

    def __init__(
        self,
        channels: _ChannelRegistry = None,
        enums: _EnumRegistry = None,
        values: ValueMap = None,
        fields: _Iterable[_BitFields] = None,
    ) -> None:
        """Initialize this channel environment."""

        super().__init__()

        if channels is None:
            channels = _ChannelRegistry()
        if enums is None:
            enums = _EnumRegistry()

        self.channels = channels
        self.enums = enums
        self.fields = _BitFieldsManager(channels.names, enums, fields=fields)

        # Keep a mapping of each channel's name and integer identifier to the
        # underlying enumeration.
        self.channel_enums: _Dict[_AnyChannel, _RuntimeEnum] = {
            chan: self.enums[chan.enum]
            for chan in self.channels.items.values()
            if chan.is_enum
        }

        # Organize channel by Python type.
        self.bools: _Set[_BoolChannel] = {
            chan
            for chan in self.channels.items.values()
            if chan.type.is_boolean
        }
        self.ints: _Set[_IntChannel] = {
            chan
            for chan in self.channels.items.values()
            if chan.type.is_integer
        }
        self.floats: _Set[_FloatChannel] = {
            chan for chan in self.channels.items.values() if chan.type.is_float
        }

        # Apply initial values if they were provided.
        if values is not None:
            self.apply(values)

    def set(self, key: _RegistryKey, value: ChannelValue) -> None:
        """Attempt to set an arbitrary channel value."""

        # Set a field value if this key maps to a bit-field.
        if self.fields.has_field(key):
            assert not isinstance(value, float)
            self.fields.set(key, value)
            return

        chan, enum = self[key]

        # Resolve enum values.
        if isinstance(value, str):
            # Ensure that the channel has an associated enumeration.
            if enum is None:
                raise ValueError(
                    (
                        f"Can't assign '{value}' to channel "
                        f"'{self.channels.names.name(key)}'!"
                    )
                )

            value = (
                enum.get_bool(value)
                if chan.type.is_boolean
                else enum.get_int(value)
            )

        # Assign the value to the channel.
        chan.raw.value = value

    def apply(self, values: ValueMap) -> None:
        """Apply a map of values to the environment."""

        for key, value in values.items():
            self.set(key, value)

    def values(self, resolve_enum: bool = True) -> ValueMap:
        """Get a new dictionary of current channel values."""

        return {
            name: self.value(name, resolve_enum=resolve_enum)
            for name in self.channels.names.names
        }

    def value(
        self, key: _RegistryKey, resolve_enum: bool = True
    ) -> ChannelValue:
        """Attempt to get a channel's current value."""

        # Get the value from a field if this key points to a bit-field.
        if self.fields.has_field(key):
            return self.fields.get(key, resolve_enum=resolve_enum)

        chan, enum = self[key]

        value: ChannelValue

        # Resolve enumeration values to strings.
        if enum is not None and resolve_enum:
            value = enum.get_str(_cast(int, chan.raw.value))
        else:
            value = chan.raw.value

        return value

    def get(self, val: _RegistryKey) -> _Optional[ChannelResult]:
        """Attempt to get a channel and its enumeration (if it has one)."""

        chan = self.channels.get(val)
        if chan is None:
            return None

        enum = None
        if chan in self.channel_enums:
            enum = self.channel_enums[chan]

        return chan, enum

    def __getitem__(self, key: _RegistryKey) -> ChannelResult:
        """Get a channel and its enumeration."""

        result = self.get(key)
        if result is None:
            raise KeyError(f"No channel '{key}'!")
        return result

    def get_int(self, key: _RegistryKey) -> IntChannelResult:
        """Get an integer channel."""

        result = self[key]

        # Ensure that this is an integer channel.
        if result[0] not in self.ints:
            raise KeyError("Channel '{key}' is not integer!")

        return _cast(_IntChannel, result[0]), result[1]

    def get_bool(self, key: _RegistryKey) -> BoolChannelResult:
        """Get a boolean channel."""

        result = self[key]

        # Ensure that this is an integer channel.
        if result[0] not in self.bools:
            raise KeyError("Channel '{key}' is not boolean!")

        return _cast(_BoolChannel, result[0]), result[1]

    def get_float(self, key: _RegistryKey) -> _FloatChannel:
        """Get a floating-point channel."""

        result = self[key]
        if result[0] not in self.floats:
            raise KeyError("Channel '{key}' is not a float!")
        return _cast(_FloatChannel, result[0])

    def __eq__(self, other) -> bool:
        """Determine if two channel environments are equivalent."""
        return bool(
            self.channels == other.channels and self.enums == other.enums
        )
