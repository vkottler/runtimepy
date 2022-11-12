"""
A module implementing a basic channel interface.
"""

# built-in
from typing import Generic as _Generic
from typing import Union as _Union
from typing import cast as _cast

# third-party
from vcorelib.io.types import JsonObject as _JsonObject

# internal
from runtimepy.mixins.enum import EnumMixin as _EnumMixin
from runtimepy.primitives import T as _T
from runtimepy.primitives import normalize as _normalize
from runtimepy.primitives.bool import Bool as _Bool
from runtimepy.primitives.float import Double as _Double
from runtimepy.primitives.float import Float as _Float
from runtimepy.primitives.int import Int8 as _Int8
from runtimepy.primitives.int import Int16 as _Int16
from runtimepy.primitives.int import Int32 as _Int32
from runtimepy.primitives.int import Int64 as _Int64
from runtimepy.primitives.int import Uint8 as _Uint8
from runtimepy.primitives.int import Uint16 as _Uint16
from runtimepy.primitives.int import Uint32 as _Uint32
from runtimepy.primitives.int import Uint64 as _Uint64
from runtimepy.registry.item import RegistryItem as _RegistryItem


class Channel(_RegistryItem, _EnumMixin, _Generic[_T]):
    """An interface for an individual channel."""

    def __str__(self) -> str:
        """Get this channel as a string."""
        return f"{self.id}: {self.raw}"

    def __bool__(self) -> bool:
        """Get this channel as a boolean."""
        return bool(self.raw)

    def init(self, data: _JsonObject) -> None:
        """Perform implementation-specific initialization."""

        super().init(data)

        # This is the underlying storage entity for this channel.
        self.raw: _T = _cast(_T, _normalize(_cast(str, data["type"]))())
        self.type = self.raw.kind

        # Whether or not this channel should accept commands.
        self.commandable: bool = _cast(bool, data["commandable"])

        # A key to this channel's enumeration in the enumeration registry.
        self._enum = _cast(str, data.get("enum"))

    def asdict(self) -> _JsonObject:
        """Obtain a dictionary representing this instance."""

        result = {
            "id": self.id,
            "type": str(self.type),
            "commandable": self.commandable,
        }
        if self._enum is not None:
            result["enum"] = self._enum
        return _cast(_JsonObject, result)


# Convenient type definitions.
IntChannel = _Union[
    Channel[_Int8],
    Channel[_Int16],
    Channel[_Int32],
    Channel[_Int64],
    Channel[_Uint8],
    Channel[_Uint16],
    Channel[_Uint32],
    Channel[_Uint64],
]
FloatChannel = _Union[Channel[_Float], Channel[_Double]]
BoolChannel = Channel[_Bool]
AnyChannel = _Union[IntChannel, FloatChannel, BoolChannel]
