"""
A module implementing an interface to build communication protocols.
"""

# internal
from runtimepy.codec.protocol.json import JsonProtocol


class Protocol(JsonProtocol):
    """A class for defining runtime communication protocols."""
