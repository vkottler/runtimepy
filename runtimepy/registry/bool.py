"""
A simple boolean-to-identifier registry interface.
"""

# internal
from runtimepy.mapping import TwoWayNameMapping as _TwoWayNameMapping


class BooleanRegistry(_TwoWayNameMapping[bool]):
    """A simple class for keeping track of boolean-to-identifier mappings."""

    def register(self, name: str, value: bool) -> bool:
        """Register a new name and value pair."""

        # Ensure the name is valid and we haven't already registered this name
        # or value.
        if (
            not self.validate_name(name)
            or name in self._reverse
            or value in self._mapping
        ):
            return False

        self._mapping[value] = name
        self._reverse[name] = value
        return True
