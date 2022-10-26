"""
A module implementing and enumeration registry.
"""

# built-in
from typing import Type as _Type

# internal
from runtimepy.enum import RuntimeEnum as _RuntimeEnum
from runtimepy.registry import Registry as _Registry


class EnumRegistry(_Registry[_RuntimeEnum]):
    """A runtime enumeration registry."""

    @property
    def kind(self) -> _Type[_RuntimeEnum]:
        """Determine what kind of registry this is."""
        return _RuntimeEnum
