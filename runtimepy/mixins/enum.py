"""
A module implementing a class mixin for classes that have an optional
enum-registry key.
"""

# built-in
from typing import Optional as _Optional

# internal
from runtimepy.registry.name import RegistryKey as _RegistryKey


class EnumMixin:
    """A class for working with an underlying enum attribute."""

    # Instance initialization must set this.
    _enum: _Optional[_RegistryKey]

    @property
    def is_enum(self) -> bool:
        """Determine if this channel has an associated enumeration."""
        return self._enum is not None

    @property
    def enum(self) -> _RegistryKey:
        """Get the enum-registry key for this channel."""
        assert self._enum is not None
        return self._enum
