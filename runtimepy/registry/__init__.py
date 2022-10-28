"""
A generic registry interface for keeping track of objects by either string or
integer identifier.
"""

# built-in
from abc import abstractmethod as _abstractmethod
from typing import Dict as _Dict
from typing import Generic as _Generic
from typing import Optional as _Optional
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import cast as _cast

# third-party
from vcorelib.dict.codec import DictCodec as _DictCodec
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.io.types import JsonValue as _JsonValue
from vcorelib.schemas.base import SchemaMap as _SchemaMap

# internal
from runtimepy.registry.item import RegistryItem as _RegistryItem
from runtimepy.registry.name import NameRegistry as _NameRegistry
from runtimepy.registry.name import RegistryKey as _RegistryKey
from runtimepy.schemas import json_schemas as _json_schemas

T = _TypeVar("T", bound=_RegistryItem)


class Registry(_DictCodec, _Generic[T]):
    """A base class for a generic registry."""

    default_schemas: _Optional[_SchemaMap] = _json_schemas()
    name_registry: _Type[_NameRegistry] = _NameRegistry

    @property
    @_abstractmethod
    def kind(self) -> _Type[T]:
        """Determine what kind of registry this is."""

    def init(self, data: _JsonObject) -> None:
        """Perform implementation-specific initialization."""

        # Create the registry items and name mapping.
        self.items: _Dict[str, T] = {
            name: self.kind.create(_cast(_JsonObject, data))
            for name, data in data.items()
        }

        # Create the name registry.
        self.names = self.name_registry(
            reverse={name: item.id for name, item in self.items.items()}
        )

    def asdict(self) -> _JsonObject:
        """Get this registry as a dictionary."""

        return {
            name: _cast(_JsonValue, item.asdict())
            for name, item in self.items.items()
        }

    def register(self, name: str, item: T) -> bool:
        """Attempt to register a new item."""

        identifier = self.names.register_name(name, identifier=item.id)

        added = False
        if identifier is not None and name not in self.items:
            self.items[name] = item
            added = True
        return added

    def register_dict(self, name: str, data: _JsonObject) -> _Optional[T]:
        """Register a new item from dictionary data."""

        # Inject an identifier into the data if one's not present.
        if "id" not in data:
            identifier = self.names.register_name(name)
            if identifier is None:
                return None
            data["id"] = identifier

        item = self.kind(data)
        result = self.register(name, item)
        return item if result else None

    def get(self, key: _RegistryKey) -> _Optional[T]:
        """Attempt to get an item from a registry key."""

        result = None
        name = self.names.name(key)
        if name is not None:
            result = self.items[name]
        return result

    def __getitem__(self, key: _RegistryKey) -> T:
        """Get a registry item."""

        item = self.get(key)
        if item is None:
            raise KeyError(f"No item '{key}'!")
        return item
