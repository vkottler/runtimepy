"""
A module implementing a basic channel interface.
"""

# built-in
from typing import Generic as _Generic
from typing import Optional as _Optional
from typing import Union as _Union
from typing import cast as _cast

# third-party
from vcorelib.io.types import JsonObject as _JsonObject

# internal
from runtimepy.channel.event import PrimitiveEvent
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
from runtimepy.primitives.types import AnyPrimitiveType as _AnyPrimitiveType
from runtimepy.registry.item import RegistryItem as _RegistryItem

Literal = int | float | bool
Default = _Optional[Literal]
Controls = dict[str, Literal | dict[str, Literal]]


class Channel(_RegistryItem, _EnumMixin, _Generic[_T]):
    """An interface for an individual channel."""

    raw: _T
    default: Default

    def __str__(self) -> str:
        """Get this channel as a string."""
        return f"{self.id}: {self.raw}"

    def __bool__(self) -> bool:
        """Get this channel as a boolean."""
        return bool(self.raw)

    @property
    def has_default(self) -> bool:
        """Determine if this channel has a default value configured."""
        return self.default is not None

    @property
    def type(self) -> _AnyPrimitiveType:
        """Get the underlying primitive type of this channel."""
        return self.raw.kind

    def update_primitive(self, primitive: _T) -> None:
        """Use a new underlying primitive for this channel."""

        assert isinstance(primitive, type(self.raw))
        self.raw = primitive

        # Update other runtime pieces.
        self.event.primitive = self.raw
        self.set_default()

    def set_default(self, default: Default = None) -> None:
        """Set a new default value for this channel."""

        if default is not None:
            self.default = default

        if self.default is not None:
            assert self.raw.valid_primitive(self.default), (
                self.raw,
                self.default,
            )
            self.raw.value = self.default  # type: ignore

    def init(self, data: _JsonObject) -> None:
        """Perform implementation-specific initialization."""

        super().init(data)

        # This is the underlying storage entity for this channel.
        self.raw: _T = _cast(_T, _normalize(_cast(str, data["type"]))())

        _ctl: _Optional[Controls] = data.get("controls")  # type: ignore
        self.controls: _Optional[Controls] = _ctl

        # Handle a possible default value.
        backup = None
        self.default = backup
        if _ctl:
            backup = _ctl.get("default")
        self.set_default(data.get("default", backup))  # type: ignore

        # Whether or not this channel should accept commands.
        self.commandable: bool = _cast(bool, data["commandable"])

        # A key to this channel's enumeration in the enumeration registry.
        self._enum = _cast(str, data.get("enum"))

        self.description: _Optional[str] = _cast(str, data.get("description"))

        # An event-streaming interface.
        self.event = PrimitiveEvent(self.raw, self.id)

    def asdict(self) -> _JsonObject:
        """Obtain a dictionary representing this instance."""

        result = {
            "id": self.id,
            "type": str(self.type),
            "commandable": self.commandable,
        }

        if self._enum is not None:
            result["enum"] = self._enum

        if self.controls:
            result["controls"] = self.controls

        if self.description:
            result["description"] = self.description
        if self.default is not None:
            result["default"] = self.default

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
