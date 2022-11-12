"""
A module implementing a runtime enumeration interface.
"""

# built-in
from typing import Optional as _Optional
from typing import Union as _Union
from typing import cast as _cast

# third-party
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.io.types import JsonValue as _JsonValue

# internal
from runtimepy.enum.type import EnumType as _EnumType
from runtimepy.mapping import BoolMappingData as _BoolMappingData
from runtimepy.mapping import IntMappingData as _IntMappingData
from runtimepy.registry.bool import BooleanRegistry as _BooleanRegistry
from runtimepy.registry.item import RegistryItem as _RegistryItem
from runtimepy.registry.name import NameRegistry as _NameRegistry


class RuntimeEnum(_RegistryItem):
    """A class implementing a runtime enumeration."""

    @property
    def is_boolean(self) -> bool:
        """Determine if this is a boolean enumeration."""
        return self._bools is not None

    @property
    def is_integer(self) -> bool:
        """Determine if this is an integer enumeration."""
        return self._ints is not None

    @property
    def ints(self) -> _NameRegistry:
        """Get the underlying integer enumeration."""
        assert self._ints is not None, "Not an integer enumeration!"
        return self._ints

    @property
    def bools(self) -> _BooleanRegistry:
        """Get the underlying boolean enumeration."""
        assert self._bools is not None, "Not a boolean enumeration!"
        return self._bools

    def init(self, data: _JsonObject) -> None:
        """Perform implementation-specific initialization."""

        super().init(data)

        self.type = _EnumType.normalize(str(data["type"]))

        # Use distinct storage attributes for each kind of underlying
        # enumeration.
        self._ints: _Optional[_NameRegistry] = None
        self._bools: _Optional[_BooleanRegistry] = None

        # It's not required for an enumeration to start with entries.
        data.setdefault("items", {})

        if self.type is _EnumType.INT:
            self._ints = _NameRegistry.int_from_dict(
                _cast(_IntMappingData, data["items"])
            )
        else:
            self._bools = _BooleanRegistry.bool_from_dict(
                _cast(_BoolMappingData, data["items"])
            )

    def asdict(self) -> _JsonObject:
        """Obtain a dictionary representing this instance."""

        result: _JsonObject = {"id": self.id, "type": str(self.type)}
        if self.is_integer:
            result["items"] = _cast(_JsonValue, self.ints.asdict())
        else:
            assert self._bools is not None
            result["items"] = _cast(_JsonValue, self.bools.asdict())

        return result

    def as_str(self, value: _Union[str, bool, int]) -> _Optional[str]:
        """Attempt to get an enumeration string."""

        if self.is_integer:
            result = self.ints.name(value)
        else:
            result = self.bools.name(_cast(bool, value))

        return result

    def get_str(self, value: _Union[str, bool, int]) -> str:
        """Get an enumeration string."""

        result = self.as_str(value)
        if result is None:
            raise KeyError(f"No enum entry for '{value}'")
        return result

    def as_int(self, value: _Union[str, int]) -> _Optional[int]:
        """Attempt to get an enumeration integer."""
        return self.ints.identifier(value)

    def get_int(self, value: _Union[str, int, bool]) -> int:
        """Get an enumeration integer."""

        result: _Union[int, bool, None] = None
        if self._ints is not None:
            result = self.as_int(value)

        # Allow a boolean enumeration to also resolve integer values.
        if self._bools is not None:
            result = self.as_bool(_cast(bool, value))

        if result is None:
            raise KeyError(f"No enum entry for '{value}'")

        return int(result)

    def as_bool(self, value: _Union[str, bool]) -> _Optional[bool]:
        """Attempt to get an enumeration boolean."""
        return self.bools.identifier(value)

    def get_bool(self, value: _Union[str, bool]) -> bool:
        """Get an enumeration boolean."""

        result = self.as_bool(value)
        if result is None:
            raise KeyError(f"No enum entry for '{value}'")
        return result

    def register_int(self, name: str) -> _Optional[int]:
        """Register an integer enumeration."""
        return self.ints.register_name(name)

    def register_bool(self, name: str, value: bool) -> bool:
        """Register a boolean enumeration."""
        return self.bools.register(name, value)
