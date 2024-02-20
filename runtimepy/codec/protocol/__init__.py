"""
A module implementing an interface to build communication protocols.
"""

# built-in
from abc import ABC, abstractmethod
from copy import copy

# internal
from runtimepy.codec.protocol.json import JsonProtocol
from runtimepy.enum.registry import EnumRegistry


class Protocol(JsonProtocol):
    """A class for defining runtime communication protocols."""


class ProtocolFactory(ABC):
    """
    A class implementing an interface for creating runtime instances of a
    prototypes that are unique to the implementing class.
    """

    # Can be re-assigned during inheriting class declaration.
    protocol: Protocol = Protocol(EnumRegistry())
    initialized = False

    @classmethod
    @abstractmethod
    def initialize(cls, protocol: Protocol) -> None:
        """Initialize this protocol."""

    @classmethod
    def instance(cls) -> Protocol:
        """Create an instance of this factory's protocol."""

        # We only need to run the routine that populates the protocol once.
        if not cls.initialized:
            cls.initialize(cls.protocol)
            cls.initialized = True

        return copy(cls.protocol)
