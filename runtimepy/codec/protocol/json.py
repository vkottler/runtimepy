"""
A protocol extension for importing and exporting JSON.
"""

# built-in
from json import dumps as _dumps
from typing import BinaryIO as _BinaryIO
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
META_KEY = "meta"
T = _TypeVar("T", bound="JsonProtocol")


class JsonProtocol(ProtocolBase):
    """A class for defining runtime communication protocols."""

    def meta_str(self, resolve_enum: bool = True) -> str:
        """Get protocol metadata as a string.."""
        return _dumps(self.export_json(resolve_enum=resolve_enum))

    def meta_bytes(self, resolve_enum: bool = True) -> bytes:
        """Get protocol metadata as a bytes object."""
        return self.meta_str(resolve_enum=resolve_enum).encode()

    def write_meta(self, stream: _BinaryIO, resolve_enum: bool = True) -> int:
        """Write protocol metadata to a stream."""
        return stream.write(self.meta_bytes(resolve_enum=resolve_enum))

    def export_json(self, resolve_enum: bool = True) -> dict[str, _JsonObject]:
        """Export this protocol's data to JSON."""

        data = self._fields.export_json(resolve_enum=resolve_enum)
        data[META_KEY] = {
            "id": self.id,
            "byte_order": self.array.byte_order.name.lower(),
        }

        # Export regular-field names.
        json_obj = data[NAMES_KEY]
        json_obj.update(
            {
                name: self.names.identifier(name)
                for name in self._regular_fields
            }
        )

        # Export enums used by regular fields.
        enum_ids: set[int] = {x.id for x in self._enum_fields.values()}
        json_obj = data[ENUMS_KEY]
        json_obj.update(
            {
                name: _cast(_JsonValue, val.asdict())
                for name, val in self._enum_registry.items.items()
                if val.id in enum_ids and name not in json_obj
            }
        )

        # Export the build specification.
        build: list[_Union[int, _JsonObject, str]] = []
        for item in self._build:
            if isinstance(item, (int, str)):
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
    def import_json(cls: type[T], data: dict[str, _JsonObject]) -> T:
        """Create a bit-fields manager from JSON data."""

        # Only set values once (at the end).
        values = data.get(VALUES_KEY, {})
        if VALUES_KEY in data:
            del data[VALUES_KEY]

        fields = BitFieldsManager.import_json(data)

        # Create the build specification.
        build: list[_Union[int, FieldSpec, str]] = []
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

        result = cls(
            fields.enums,
            fields.registry,
            fields=fields,
            build=build,
            identifier=_cast(int, data[META_KEY]["id"]),
            byte_order=_cast(str, data[META_KEY]["byte_order"]),
        )

        # Set values.
        for name, value in values.items():
            result[name] = _cast(int, value)

        return result
