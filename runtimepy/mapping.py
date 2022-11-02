"""
A module implementing a generic, two-way mapping interface.
"""

# built-in
from typing import Generic as _Generic
from typing import MutableMapping as _MutableMapping
from typing import Optional as _Optional
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import Union as _Union
from typing import cast as _cast

# internal
from runtimepy.mixins.regex import RegexMixin as _RegexMixin

# This determines types that are valid as keys.
T = _TypeVar("T", int, bool)

KeyToName = _MutableMapping[T, str]
NameToKey = _MutableMapping[str, T]
MappingKey = _Union[str, T]

IntMapping = _TypeVar("IntMapping", bound="TwoWayNameMapping[int]")
BoolMapping = _TypeVar("BoolMapping", bound="TwoWayNameMapping[bool]")

IntMappingData = _MutableMapping[MappingKey[int], MappingKey[int]]
BoolMappingData = _MutableMapping[MappingKey[bool], MappingKey[bool]]
EnumMappingData = _Union[
    IntMappingData,
    BoolMappingData,
    _MutableMapping[str, bool],
    _MutableMapping[str, int],
]


class TwoWayNameMapping(_RegexMixin, _Generic[T]):
    """A class interface for managing two-way mappings."""

    def __init__(
        self,
        mapping: KeyToName[T] = None,
        reverse: NameToKey[T] = None,
    ) -> None:
        """Initialize this name registry."""

        if mapping is None:
            mapping = {}
        if reverse is None:
            reverse = {}

        self._mapping: KeyToName[T] = mapping
        self._reverse: NameToKey[T] = reverse

        # Populate the reverse mapping.
        for key, name in self._mapping.items():
            if name not in self._reverse:
                self._reverse[name] = key
            else:
                # Ensure the mappings are consistent.
                assert self._reverse[name] == key

        # Populate the forward mapping.
        for name, key in self._reverse.items():
            if key not in self._mapping:
                self._mapping[key] = name
            else:
                # Ensure the mappings are consistent.
                assert self._mapping[key] == name

        # Validate names.
        for name in self._reverse:
            assert self.validate_name(name), f"Invalid name '{name}'!"

    def identifier(self, key: MappingKey[T]) -> _Optional[T]:
        """Get the integer identifier associated with a registry key."""

        if isinstance(key, str):
            return self._reverse.get(key)
        if key in self._mapping:
            return key

        return None

    def name(self, key: MappingKey[T]) -> _Optional[str]:
        """Get the name associated with a registry key."""

        if isinstance(key, str):
            if key in self._reverse:
                return key

        return self._mapping.get(_cast(T, key))

    def asdict(self) -> NameToKey[T]:
        """Provide a dictionary representation."""
        return self._reverse

    @classmethod
    def int_from_dict(
        cls: _Type[IntMapping], data: IntMappingData
    ) -> IntMapping:
        """
        Create an integer-to-name mapping from a dictionary with arbitrary
        data.
        """

        mapping: KeyToName[int] = {}
        reverse: NameToKey[int] = {}

        # Set forward and reverse mapping values for the constructor.
        for key, value in data.items():
            if isinstance(key, str):
                reverse[key] = int(value)
            else:
                mapping[key] = str(value)

        return cls(mapping=mapping, reverse=reverse)

    @classmethod
    def bool_from_dict(
        cls: _Type[BoolMapping], data: BoolMappingData
    ) -> BoolMapping:
        """
        Create a boolean-to-name mapping from a dictionary with arbitrary data.
        """

        mapping: KeyToName[bool] = {}
        reverse: NameToKey[bool] = {}

        # Set forward and reverse mapping values for the constructor.
        for key, value in data.items():
            if isinstance(key, str):
                reverse[key] = bool(value)
            else:
                mapping[key] = str(value)

        return cls(mapping=mapping, reverse=reverse)
