"""
A module implementing an interface for items that can belong to registries.
"""

# built-in
from abc import abstractmethod as _abstractmethod

# third-party
from vcorelib.dict.codec import DictCodec as _DictCodec


class RegistryItem(_DictCodec):
    """A class interface for items that can be managed via a registry."""

    @property
    @_abstractmethod
    def id(self) -> int:
        """Get this registry item's identifier."""

    def __hash__(self) -> int:
        """Get a suitable hash for this registry item."""
        return hash(self.id)

    def __eq__(self, other) -> bool:
        """Use the integer identifier to determine equivalence."""
        return bool(self.id == getattr(other, "id", other["id"]))
