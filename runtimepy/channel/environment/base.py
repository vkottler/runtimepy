"""
A module implementing a base channel environment.
"""

# built-in
from typing import Iterable as _Iterable
from typing import Optional as _Optional
from typing import Union as _Union
from typing import cast as _cast

# third-party
from vcorelib.namespace import DEFAULT_DELIM, Namespace
from vcorelib.namespace import NamespaceMixin as _NamespaceMixin

# internal
from runtimepy.channel import AnyChannel as _AnyChannel
from runtimepy.channel import BoolChannel as _BoolChannel
from runtimepy.channel import FloatChannel as _FloatChannel
from runtimepy.channel import IntChannel as _IntChannel
from runtimepy.channel.registry import ChannelRegistry as _ChannelRegistry
from runtimepy.enum import RuntimeEnum as _RuntimeEnum
from runtimepy.enum.registry import EnumRegistry as _EnumRegistry
from runtimepy.mixins.finalize import FinalizeMixin
from runtimepy.primitives import StrToBool
from runtimepy.primitives.field import BitField as _BitField
from runtimepy.primitives.field.fields import BitFields as _BitFields
from runtimepy.primitives.field.manager import (
    BitFieldsManager as _BitFieldsManager,
)
from runtimepy.registry.name import RegistryKey as _RegistryKey

ChannelValue = _Union[bool, int, float, str]
ValueMap = dict[_RegistryKey, ChannelValue]

ChannelResult = tuple[_AnyChannel, _Optional[_RuntimeEnum]]
BitfieldResult = tuple[_BitField, _Optional[_RuntimeEnum]]
BoolChannelResult = tuple[_BoolChannel, _Optional[_RuntimeEnum]]
IntChannelResult = tuple[_IntChannel, _Optional[_RuntimeEnum]]

FieldOrChannel = _Union[_BitField, _AnyChannel]


class BaseChannelEnvironment(_NamespaceMixin, FinalizeMixin):
    """A class integrating channel and enumeration registries."""

    def __init__(
        self,
        channels: _ChannelRegistry = None,
        enums: _EnumRegistry = None,
        values: ValueMap = None,
        fields: _Iterable[_BitFields] = None,
        namespace: Namespace = None,
        namespace_delim: str = DEFAULT_DELIM,
    ) -> None:
        """Initialize this channel environment."""

        _NamespaceMixin.__init__(
            self, namespace=namespace, namespace_delim=namespace_delim
        )
        FinalizeMixin.__init__(self)

        if channels is None:
            channels = _ChannelRegistry()
        if enums is None:
            enums = _EnumRegistry()

        self.channels = channels
        self.enums = enums

        # Register fields.
        self.fields = _BitFieldsManager(channels.names, self.enums)
        if fields:
            for field in fields:
                self.fields.add(field)

        self.to_add: list[_BitFields] = []

        # Keep a mapping of each channel's name and integer identifier to the
        # underlying enumeration.
        self.channel_enums: dict[_AnyChannel, _RuntimeEnum] = {
            chan: self.enums[chan.enum]
            for chan in self.channels.items.values()
            if chan.is_enum
        }

        # Organize channel by Python type.
        self.bools: set[_BoolChannel] = {
            chan
            for chan in self.channels.items.values()
            if chan.type.is_boolean
        }
        self.ints: set[_IntChannel] = {
            chan
            for chan in self.channels.items.values()
            if chan.type.is_integer
        }
        self.floats: set[_FloatChannel] = {
            chan for chan in self.channels.items.values() if chan.type.is_float
        }

        # Apply initial values if they were provided.
        if values is not None:
            self.apply(values)

    def __setitem__(self, key: _RegistryKey, value: ChannelValue) -> None:
        """Mapping-set interface."""
        return self.set(key, value)

    def set(
        self, key: _RegistryKey, value: ChannelValue, scaled: bool = True
    ) -> None:
        """Attempt to set an arbitrary channel value."""

        # Set a field value if this key maps to a bit-field.
        if self.fields.has_field(key):
            assert not isinstance(value, float)
            self.fields.set(key, value, scaled=scaled)
            return

        chan, enum = self[key]

        # Resolve enum values.
        if isinstance(value, str):
            # Ensure that the channel has an associated enumeration.
            if enum is None:
                resolved = False

                is_int = chan.raw.kind.is_integer

                if is_int or chan.raw.kind.is_float:
                    kind = int if is_int and not chan.raw.scaling else float
                    try:
                        value = kind(value)
                        resolved = True
                    except ValueError:
                        pass

                # Handle booleans.
                else:
                    parsed = StrToBool.parse(value)
                    value = parsed.result
                    resolved = parsed.valid

                if not resolved:
                    raise ValueError(
                        (
                            f"Can't assign '{value}' to channel "
                            f"'{self.channels.names.name(key)}'!"
                        )
                    )

            else:
                value = (
                    enum.get_bool(value)
                    if chan.type.is_boolean
                    else enum.get_int(value)
                )

        # Assign the value to the channel.
        if scaled:
            chan.raw.scaled = value  # type: ignore
        else:
            chan.raw.value = value  # type: ignore

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
        self, key: _RegistryKey, resolve_enum: bool = True, scaled: bool = True
    ) -> ChannelValue:
        """Attempt to get a channel's current value."""

        # Get the value from a field if this key points to a bit-field.
        if self.fields.has_field(key):
            return self.fields.get(
                key, resolve_enum=resolve_enum, scaled=scaled
            )

        chan, enum = self[key]

        value: ChannelValue = chan.raw.scaled if scaled else chan.raw.value

        # Resolve enumeration values to strings.
        if enum is not None and resolve_enum:
            value = enum.get_str(_cast(int, value))

        return value

    def exists(self, val: _RegistryKey) -> bool:
        """Determine if a channel exists."""
        return self.fields.has_field(val) or self.get(val) is not None

    def field_or_channel(self, val: _RegistryKey) -> _Optional[FieldOrChannel]:
        """Attempt to look up a field or channel for a given registry key."""

        channel: _Optional[FieldOrChannel] = None

        chan = self.get(val)
        if chan is None:
            # Check if the name is a field.
            field = self.fields.get_field(val)
            if field is not None:
                channel = field
        else:
            channel, _ = chan

        return channel

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

    def add_int(self, key: _RegistryKey, amount: int) -> int:
        """Modify an integer channel."""

        chan = self.get_int(key)[0]
        chan.raw.value += amount
        return chan.raw.value

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

    def age_ns(self, key: _RegistryKey) -> int:
        """Get the age of an entity based on registry key."""

        chan = self.get(key)
        if chan is not None:
            prim = chan[0].raw
        else:
            prim = self.fields[key].raw

        return prim.age_ns()

    def add_field(self, field: _BitField, namespace: Namespace = None) -> str:
        """Add a bit field to the environment."""

        result = self.fields.add_field(field)
        if result is not None:
            self.to_add.append(result)

        return self.namespace(name=field.name, namespace=namespace)

    def finalize(self, strict: bool = True) -> None:
        """Finalize this instance."""

        for fields in self.to_add:
            self.fields.add(fields)

        super().finalize(strict=strict)
