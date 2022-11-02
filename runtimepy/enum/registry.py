"""
A module implementing and enumeration registry.
"""

# built-in
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
