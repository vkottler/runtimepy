"""
A module implementing interfaces related to channel-protocol headers.
"""

# internal
from runtimepy.codec.protocol import Protocol, ProtocolFactory
from runtimepy.primitives import Uint16

IdType = Uint16
ID_SINGLE = IdType()


class PrimitiveEventHeader(ProtocolFactory):
    """A protocol for implementing channel events."""

    @classmethod
    def initialize(cls, protocol: Protocol) -> None:
        """Initialize this protocol."""

        protocol.add_field("identifier", kind=IdType)
        protocol.add_field("timestamp", kind="uint64")

    @classmethod
    def init_header(cls, protocol: Protocol, identifier: int) -> None:
        """Initialize a channel-event header."""

        bounds = ID_SINGLE.kind.int_bounds
        assert bounds is not None
        assert bounds.validate(identifier), identifier
        protocol["identifier"] = identifier
