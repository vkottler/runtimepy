"""
A channel-environment extension for loading and saving files.
"""

# built-in
from typing import Optional as _Optional
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import cast as _cast

# third-party
from vcorelib.io import ARBITER as _ARBITER
from vcorelib.io.types import JsonObject as _JsonObject
from vcorelib.paths import Pathlike as _Pathlike
from vcorelib.paths import normalize as _normalize

# internal
from runtimepy.channel.environment.base import (
    BaseChannelEnvironment as _BaseChannelEnvironment,
)
from runtimepy.channel.environment.base import ValueMap as _ValueMap
from runtimepy.channel.registry import ChannelRegistry as _ChannelRegistry
from runtimepy.enum.registry import EnumRegistry as _EnumRegistry
from runtimepy.primitives.field.manager import (
    fields_from_file as _fields_from_file,
)

T = _TypeVar("T", bound="FileChannelEnvironment")
CHANNELS_FILE = "channels.json"
ENUMS_FILE = "enums.json"
VALUES_FILE = "values.json"
FIELDS_FILE = "fields.json"
NAMES_FILE = "names.json"


class FileChannelEnvironment(_BaseChannelEnvironment):
    """A class integrating file-system operations with channel environments."""

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
                    "channels": self.channels.names.asdict(),
                    "enums": self.enums.names.asdict(),
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
    def load(
        cls: _Type[T],
        channels: _Pathlike = CHANNELS_FILE,
        enums: _Pathlike = ENUMS_FILE,
        values: _Pathlike = VALUES_FILE,
        fields: _Pathlike = FIELDS_FILE,
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
        )
