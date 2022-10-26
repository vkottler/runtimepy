"""
A simple name-to-identifier registry interface.
"""

# built-in
from typing import MutableMapping as _MutableMapping
from typing import Optional as _Optional
from typing import Union as _Union

# internal
from runtimepy.mapping import TwoWayNameMapping as _TwoWayNameMapping

RegistryKey = _Union[str, int]
KeyToName = _MutableMapping[int, str]
NameToKey = _MutableMapping[str, int]


class NameRegistry(_TwoWayNameMapping[int]):
    """A simple class for keeping track of name-to-identifier mappings."""

    def __init__(
        self,
        mapping: KeyToName = None,
        reverse: NameToKey = None,
    ) -> None:
        """Initialize this name registry."""

        super().__init__(mapping=mapping, reverse=reverse)
        self._current = 1

        # Ensure the next-available key does not conflict with an existing
        # entry.
        for key in self._mapping:
            if key >= self._current:
                self._current = key + 1

    def register_name(
        self, name: str, identifier: int = None
    ) -> _Optional[int]:
        """Register a new name."""

        # Ensure the name is valid.
        if not self.validate_name(name):
            return None

        # Find the next valid identifier.
        if identifier is None:
            while self._current in self._mapping:
                self._current += 1
            identifier = self._current

        # Store the mapping and return the identifier.
        if identifier not in self._mapping:
            self._mapping[identifier] = name
            self._reverse[name] = identifier
            return identifier

        # If this name is already registered, return the identifier.
        if self._reverse.get(name) == identifier:
            return identifier

        return None
