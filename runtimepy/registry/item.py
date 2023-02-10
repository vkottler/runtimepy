"""
A module implementing an interface for items that can belong to registries.
"""

# built-in
from typing import cast as _cast

# third-party
from vcorelib.io.types import JsonObject as _JsonObject

# internal
from runtimepy.schemas import RuntimepyDictCodec as _RuntimepyDictCodec


class RegistryItem(_RuntimepyDictCodec):
    """A class interface for items that can be managed via a registry."""

    def __hash__(self) -> int:
        """Get a suitable hash for this registry item."""
        return hash(self.id)

    def __eq__(self, other) -> bool:
        """Use the integer identifier to determine equivalence."""
        return bool(self.id == getattr(other, "id", other["id"]))

    def init(self, data: _JsonObject) -> None:
        """Perform implementation-specific initialization."""
        self.id: int = int(_cast(int, data["id"]))
