"""
A module implementing a generic, two-way mapping interface.
"""

# built-in
from typing import Generic as _Generic
from typing import Iterator
from typing import MutableMapping as _MutableMapping
from typing import Optional as _Optional
from typing import TypeVar as _TypeVar
from typing import Union as _Union
from typing import cast as _cast

# third-party
from vcorelib.logging import LoggerMixin
from vcorelib.names import name_search

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
DEFAULT_PATTERN = ".*"


class TwoWayNameMapping(_RegexMixin, LoggerMixin, _Generic[T]):
    """A class interface for managing two-way mappings."""

    def __init__(
        self,
        mapping: KeyToName[T] = None,
        reverse: NameToKey[T] = None,
    ) -> None:
        """Initialize this name registry."""

        self._mapping: dict[T, str] = {}
        self._reverse: dict[str, T] = {}
        self.registered_order: list[str] = []
        LoggerMixin.__init__(self)

        if mapping is not None:
            self.load_key_to_name(mapping)
        if reverse is not None:
            self.load_name_to_key(reverse)

    def _set(self, key: T, name: str) -> None:
        """Set a key<->name pairing."""

        assert self.validate_name(name), f"Invalid name '{name}'!"

        # Add to the key->name mapping.
        if key not in self._mapping:
            self._mapping[key] = name
        else:
            # Ensure the mappings are consistent.
            curr_name = self._mapping[key]
            assert curr_name == name, f"{curr_name} != {name} ({key})"

        # Add to the name->key mapping.
        if name not in self._reverse:
            self._reverse[name] = key
            self.registered_order.append(name)
        else:
            # Ensure the mappings are consistent.
            curr_key = self._reverse[name]
            assert curr_key == key, f"{curr_key} != {key} ({name})"

    def load_key_to_name(self, mapping: KeyToName[T]) -> None:
        """Load a key-to-name mapping."""
        for key, name in mapping.items():
            self._set(key, name)

    def load_name_to_key(self, reverse: NameToKey[T]) -> None:
        """Load a name-to-key mapping."""
        for name, key in reverse.items():
            self._set(key, name)

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

    @property
    def names(self) -> Iterator[str]:
        """Iterate over names."""
        yield from self._reverse

    def asdict(self) -> dict[str, T]:
        """Provide a dictionary representation."""
        return self._reverse

    @classmethod
    def int_from_dict(
        cls: type[IntMapping], data: IntMappingData
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

    def search(self, pattern: str, exact: bool = False) -> Iterator[str]:
        """Get names in this mapping based on a pattern."""
        yield from name_search(self.names, pattern, exact=exact)

    @classmethod
    def bool_from_dict(
        cls: type[BoolMapping], data: BoolMappingData
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
