"""
A management entity for bit-fields.
"""

# built-in
from typing import Iterable as _Iterable
from typing import cast as _cast

# third-party
from vcorelib.io import ARBITER as _ARBITER
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.io.types import JsonValue as _JsonValue
from vcorelib.paths import Pathlike as _Pathlike

# internal
from runtimepy.enum.registry import EnumRegistry as _EnumRegistry
from runtimepy.primitives.field.fields import BitFields as _BitFields
from runtimepy.primitives.field.manager.base import BitFieldsManagerBase
from runtimepy.registry.name import NameRegistry as _NameRegistry

NAMES_KEY = "names"
ENUMS_KEY = "enums"
FIELDS_KEY = "fields"
VALUES_KEY = "values"


def fields_from_dict(data: _JsonObject) -> _Iterable[_BitFields]:
    """Load bit-fields from JSON data."""

    return [
        _BitFields.create(x)
        for x in _cast(_Iterable[_JsonObject], data["items"])
    ]


def fields_from_file(path: _Pathlike) -> _Iterable[_BitFields]:
    """Load bit-fields from a file."""

    return fields_from_dict(_ARBITER.decode(path, require_success=True).data)


class BitFieldsManager(BitFieldsManagerBase):
    """A class for managing multiple bit-fields objects."""

    def export_json(self, resolve_enum: bool = True) -> dict[str, _JsonObject]:
        """Export this manager's data to JSON."""

        # Only export names that we're using.
        names: _JsonObject = {
            name: self.registry.identifier(name) for name in self.lookup
        }

        # Only export enums that we're using.
        enum_ids: set[int] = {x.id for x in self.enums.items.values()}
        enums: _JsonObject = {
            name: _cast(_JsonValue, val.asdict())
            for name, val in self.enums.items.items()
            if val.id in enum_ids
        }

        return {
            NAMES_KEY: names,
            ENUMS_KEY: enums,
            FIELDS_KEY: self.asdict(),
            VALUES_KEY: _cast(
                _JsonObject, self.values(resolve_enum=resolve_enum)
            ),
        }

    @classmethod
    def import_json(cls, data: dict[str, _JsonObject]) -> "BitFieldsManager":
        """Create a bit-fields manager from JSON data."""

        result = cls(
            _NameRegistry(reverse=_cast(dict[str, int], data[NAMES_KEY])),
            _EnumRegistry.create(data[ENUMS_KEY]),
            fields=fields_from_dict(data[FIELDS_KEY]),
        )

        # Set values.
        for name, value in data.get(VALUES_KEY, {}).items():
            result.set(name, _cast(int, value))

        return result
