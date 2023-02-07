"""
A channel-environment extension for loading and saving files.
"""

# built-in
from typing import Dict as _Dict
from typing import Optional as _Optional
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import cast as _cast

# third-party
from vcorelib.io import ARBITER as _ARBITER
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.io.types import JsonValue as _JsonValue
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import normalize as _normalize

# internal
from runtimepy.channel.environment.base import (
    BaseChannelEnvironment as _BaseChannelEnvironment,
)
from runtimepy.channel.environment.base import ValueMap as _ValueMap
from runtimepy.channel.registry import ChannelRegistry as _ChannelRegistry
from runtimepy.enum.registry import EnumRegistry as _EnumRegistry
from runtimepy.mapping import NameToKey as _NameToKey
from runtimepy.primitives.field.manager import (
    ENUMS_KEY,
    FIELDS_KEY,
    NAMES_KEY,
    VALUES_KEY,
)
from runtimepy.primitives.field.manager import (
    fields_from_dict as _fields_from_dict,
)
from runtimepy.primitives.field.manager import (
    fields_from_file as _fields_from_file,
)

T = _TypeVar("T", bound="FileChannelEnvironment")
CHANNELS_KEY = "channels"
CHANNELS_FILE = f"{CHANNELS_KEY}.json"
ENUMS_FILE = f"{ENUMS_KEY}.json"
VALUES_FILE = f"{VALUES_KEY}.json"
FIELDS_FILE = f"{FIELDS_KEY}.json"
NAMES_FILE = f"{NAMES_KEY}.json"


class FileChannelEnvironment(_BaseChannelEnvironment):
    """A class integrating file-system operations with channel environments."""

    def export_json(
        self, resolve_enum: bool = True
    ) -> _Dict[str, _JsonObject]:
        """Get this channel environment as a single dictionary."""

        return {
            CHANNELS_KEY: self.channels.asdict(),
            ENUMS_KEY: self.enums.asdict(),
            FIELDS_KEY: self.fields.asdict(),
            NAMES_KEY: {
                CHANNELS_KEY: _cast(_JsonValue, self.channels.names.asdict()),
                ENUMS_KEY: _cast(_JsonValue, self.enums.names.asdict()),
            },
            VALUES_KEY: _cast(
                _JsonObject, self.values(resolve_enum=resolve_enum)
            ),
        }

    def export(
        self,
        channels: _Pathlike = CHANNELS_FILE,
        enums: _Pathlike = ENUMS_FILE,
        values: _Pathlike = VALUES_FILE,
        fields: _Pathlike = FIELDS_FILE,
        names: _Pathlike = NAMES_FILE,
        resolve_enum: bool = True,
        **kwargs,
    ) -> None:
        """Write channel and enum registries to disk."""

        self.channels.encode(channels, **kwargs)
        self.enums.encode(enums, **kwargs)
        self.fields.encode(fields, **kwargs)

        # Keep track of name-to-identifier mappings for all such mappings.
        _ARBITER.encode(
            names,
            _cast(
                _JsonObject,
                {
                    CHANNELS_KEY: self.channels.names.asdict(),
                    ENUMS_KEY: self.enums.names.asdict(),
                },
            ),
            **kwargs,
        )

        _ARBITER.encode(
            values,
            _cast(_JsonObject, self.values(resolve_enum=resolve_enum)),
            **kwargs,
        )

    def export_directory(
        self, path: _Pathlike, resolve_enum: bool = True, **kwargs
    ) -> None:
        """Export this channel environment to a directory."""

        path = _normalize(path)
        path.mkdir(parents=True, exist_ok=True)
        self.export(
            channels=path.joinpath(CHANNELS_FILE),
            enums=path.joinpath(ENUMS_FILE),
            values=path.joinpath(VALUES_FILE),
            fields=path.joinpath(FIELDS_FILE),
            names=path.joinpath(NAMES_FILE),
            resolve_enum=resolve_enum,
            **kwargs,
        )

    @classmethod
    def load_json(cls: _Type[T], data: _Dict[str, _JsonObject]) -> T:
        """Load a channel environment from JSON data."""

        chan_reg = _ChannelRegistry.create(data[CHANNELS_KEY])
        enum_reg = _EnumRegistry.create(data[ENUMS_KEY])

        # Handle name data.
        chan_reg.names.load_name_to_key(
            _cast(_NameToKey[int], data[NAMES_KEY][CHANNELS_KEY])
        )
        enum_reg.names.load_name_to_key(
            _cast(_NameToKey[int], data[NAMES_KEY][ENUMS_KEY])
        )

        return cls(
            channels=chan_reg,
            enums=enum_reg,
            values=_cast(_Optional[_ValueMap], data.get(VALUES_KEY)),
            fields=_fields_from_dict(data[FIELDS_KEY]),
        )

    @classmethod
    def load(
        cls: _Type[T],
        channels: _Pathlike = CHANNELS_FILE,
        enums: _Pathlike = ENUMS_FILE,
        values: _Pathlike = VALUES_FILE,
        fields: _Pathlike = FIELDS_FILE,
        names: _Pathlike = NAMES_FILE,
    ) -> T:
        """Load a channel environment from a pair of files."""

        value_map: _Optional[_ValueMap] = None

        # Load the value map if it's present.
        values = _normalize(values)
        if values.is_file():
            value_map = _cast(
                _ValueMap, _ARBITER.decode(values, require_success=True).data
            )

        chan_reg = _ChannelRegistry.decode(channels)
        enum_reg = _EnumRegistry.decode(enums)

        # Load name-to-identifier mapping data and initialize (or update)
        # name registries.
        name_data = _ARBITER.decode(names, require_success=True).data
        chan_reg.names.load_name_to_key(
            _cast(_NameToKey[int], name_data[CHANNELS_KEY])
        )
        enum_reg.names.load_name_to_key(
            _cast(_NameToKey[int], name_data[ENUMS_KEY])
        )

        return cls(
            channels=chan_reg,
            enums=enum_reg,
            values=value_map,
            fields=_fields_from_file(fields),
        )

    @classmethod
    def load_directory(cls: _Type[T], path: _Pathlike) -> T:
        """Load a channel environment from a directory."""

        path = _normalize(path, require=True)
        assert path.is_dir(), f"'{path}' is not a directory!"
        return cls.load(
            channels=path.joinpath(CHANNELS_FILE),
            enums=path.joinpath(ENUMS_FILE),
            values=path.joinpath(VALUES_FILE),
            fields=path.joinpath(FIELDS_FILE),
            names=path.joinpath(NAMES_FILE),
        )
