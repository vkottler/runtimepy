"""
A channel-environment extension for creating arrays of primitives.
"""

# built-in
from typing import Iterable as _Iterable
from typing import NamedTuple
from typing import Optional as _Optional

# internal
from runtimepy.channel.environment.base import (
    BaseChannelEnvironment as _BaseChannelEnvironment,
)
from runtimepy.primitives.array import PrimitiveArray as _PrimitiveArray
from runtimepy.primitives.field.fields import BitFields as _BitFields
from runtimepy.registry.name import RegistryKey as _RegistryKey


class ChannelArray(NamedTuple):
    """A class for managing an array of channels and bit-fields."""

    names: list[str]
    array: _PrimitiveArray

    @staticmethod
    def create() -> "ChannelArray":
        """Create a new, empty channel array."""
        return ChannelArray([], _PrimitiveArray())


class ArrayChannelEnvironment(_BaseChannelEnvironment):
    """
    A channel-environment extension for working with arrays of primitives.
    """

    def array(self, keys: _Iterable[_RegistryKey]) -> ChannelArray:
        """
        Create a primitive array from an in-order iterable of registry keys.
        """

        result = ChannelArray.create()

        curr_fields: _Optional[_BitFields] = None
        invalid_field_names: set[str] = set()
        available_field_names: set[str] = set()

        names: set[str] = set()

        for key in keys:
            # All keys must be registered names.
            name = self.channels.names.name(key)
            assert name is not None, f"Unknown name '{key}'!"

            # Ensure channels and fields don't appear twice.
            assert name not in names, f"Name '{name}' appears twice!"
            names.add(name)
            result.names.append(name)

            # Add this channel's primitive to the array if this key maps to
            # a regular channel.
            chan_result = self.get(name)
            if chan_result is not None:
                result.array.add(chan_result[0].raw)

                # Add all available bit-field names to the invalid set now
                # that we've moved on to a non bit-field.
                invalid_field_names |= available_field_names
                available_field_names = set()
                curr_fields = None
                continue

            # If the current name doesn't appear in the set of available field
            # names, assume that we're moving on to a new primitive.
            if name not in available_field_names:
                invalid_field_names |= available_field_names
                available_field_names = set()
                curr_fields = None

            # Ensure that bit-fields belonging to primitives that have already
            # been processed don't show up later in the array registration.
            assert (
                name not in invalid_field_names
            ), f"Bit-field '{name}' is out-of-order!"

            # Begin handling a new bit-fields primitive.
            if curr_fields is None:
                fields = self.fields.get_fields(name)
                assert fields is not None, f"Unknown bit-field '{name}'!"
                result.array.add(fields.raw)
                available_field_names = set(fields.names)

            # Keep track of field names processed in the current bit-fields
            # primitive.
            available_field_names.remove(name)

        return result
