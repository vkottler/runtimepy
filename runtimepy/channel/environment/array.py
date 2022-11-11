"""
A channel-environment extension for creating arrays of primitives.
"""

# built-in
from typing import Iterable as _Iterable
from typing import Optional as _Optional

# internal
from runtimepy.channel.environment.base import (
    BaseChannelEnvironment as _BaseChannelEnvironment,
)
from runtimepy.primitives.array import PrimitiveArray as _PrimitiveArray
from runtimepy.primitives.int import UnsignedInt as _UnsignedInt
from runtimepy.registry.name import RegistryKey as _RegistryKey


class ArrayChannelEnvironment(_BaseChannelEnvironment):
    """
    A channel-environment extension for working with arrays of primitives.
    """

    def array(self, keys: _Iterable[_RegistryKey]) -> _PrimitiveArray:
        """
        Create a primitive array from an in-order iterable of registry keys.
        """

        result = _PrimitiveArray()

        curr_field_primitive: _Optional[_UnsignedInt] = None

        for key in keys:
            # Add this channel's primitive to the array if this key maps to
            # a regular channel.
            chan_result = self.get(key)
            if chan_result is not None:
                result.add(chan_result[0].raw)
                continue

            field = self.fields[key]

            if curr_field_primitive is None:
                curr_field_primitive = field.raw
                result.add(curr_field_primitive)

        return result
