"""
A protocol extension for importing and exporting JSON.
"""

# built-in
from typing import Dict as _Dict
from typing import List as _List
from typing import Set as _Set
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import Union as _Union
from typing import cast as _cast

# third-party
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.io.types import JsonValue as _JsonValue

# internal
from runtimepy.codec.protocol.base import FieldSpec, ProtocolBase
from runtimepy.primitives.field.manager import (
    ENUMS_KEY,
    NAMES_KEY,
    VALUES_KEY,
    BitFieldsManager,
)

BUILD_KEY = "build"
T = _TypeVar("T", bound="JsonProtocol")


class JsonProtocol(ProtocolBase):
    """A class for defining runtime communication protocols."""

    def export_json(
        self, resolve_enum: bool = True
    ) -> _Dict[str, _JsonObject]:
        """Export this protocol's data to JSON."""

        data = self._fields.export_json(resolve_enum=resolve_enum)

        # Export regular-field names.
        json_obj = data[NAMES_KEY]
        json_obj.update(
            {
                name: self._names.identifier(name)
                for name in self._regular_fields
            }
        )

        # Export enums used by regular fields.
        enum_ids: _Set[int] = {x.id for x in self._enum_fields.values()}
        json_obj = data[ENUMS_KEY]
        json_obj.update(
            {
                name: _cast(_JsonValue, val.asdict())
                for name, val in self._enum_registry.items.items()
                if val.id in enum_ids and name not in json_obj
            }
        )

        # Export the build specification.
        build: _List[_Union[int, _JsonObject]] = []
        for item in self._build:
            if isinstance(item, int):
                build.append(item)
            else:
                build.append(item.asdict())
        data[BUILD_KEY] = _cast(_JsonObject, build)

        # Export regular-field values.
        json_obj = data.get(VALUES_KEY, {})
        for name in self._regular_fields:
            json_obj[name] = self.value(name)
        if json_obj:
            data[VALUES_KEY] = json_obj

        return data

    @classmethod
    def import_json(cls: _Type[T], data: _Dict[str, _JsonObject]) -> T:
        """Create a bit-fields manager from JSON data."""

        # Only set values once (at the end).
        values = data.get(VALUES_KEY, {})
        if VALUES_KEY in data:
            del data[VALUES_KEY]

        fields = BitFieldsManager.import_json(data)

        # Create the build specification.
        build: _List[_Union[int, FieldSpec]] = []
        for item in data[BUILD_KEY]:
            if isinstance(item, int):
                build.append(item)
            else:
                build.append(
                    FieldSpec(
                        item["name"],  # type: ignore
                        item["kind"],  # type: ignore
                        enum=item.get("enum"),  # type: ignore
                    )
                )

        result = cls(fields.enums, fields.registry, fields=fields, build=build)

        # Set values.
        for name, value in values.items():
            result[name] = _cast(int, value)

        return result
