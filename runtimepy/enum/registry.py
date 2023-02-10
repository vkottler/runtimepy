"""
A module implementing and enumeration registry.
"""

# built-in
from enum import IntEnum as _IntEnum
from typing import Optional as _Optional
from typing import Type as _Type
from typing import cast as _cast

# third-party
from vcorelib.io.types import JsonObject as _JsonObject

# internal
from runtimepy.enum import RuntimeEnum as _RuntimeEnum
from runtimepy.enum.type import EnumTypelike as _EnumTypelike
from runtimepy.mapping import EnumMappingData as _EnumMappingData
from runtimepy.registry import Registry as _Registry


class EnumRegistry(_Registry[_RuntimeEnum]):
    """A runtime enumeration registry."""

    @property
    def kind(self) -> _Type[_RuntimeEnum]:
        """Determine what kind of registry this is."""
        return _RuntimeEnum

    def enum(
        self,
        name: str,
        kind: _EnumTypelike,
        items: _EnumMappingData = None,
    ) -> _Optional[_RuntimeEnum]:
        """Create a new runtime enumeration."""

        data: _JsonObject = {"type": _cast(str, kind)}
        if items is not None:
            data["items"] = items  # type: ignore
        return self.register_dict(name, data)


class RuntimeIntEnum(_IntEnum):
    """An integer enumeration extension."""

    @classmethod
    def runtime_enum(cls, identifier: int) -> _RuntimeEnum:
        """Obtain a runtime enumeration from this class."""
        return _RuntimeEnum.from_enum(cls, identifier)

    @classmethod
    def register_enum(
        cls, registry: EnumRegistry, name: str = None
    ) -> _RuntimeEnum:
        """Register an enumeration to a registry."""

        if name is None:
            name = cls.__name__

        result = registry.register_dict(name, _RuntimeEnum.data_from_enum(cls))
        assert result is not None
        return result
