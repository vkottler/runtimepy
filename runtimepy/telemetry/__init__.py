"""
A module implementing a telemetry interface.
"""

# internal
from runtimepy.enum.registry import RuntimeIntEnum as _RuntimeIntEnum


class MessageType(_RuntimeIntEnum):
    """An enumeration of viable message types."""

    PROTOCOL_META = 1
    PROTOCOL_DATA = 2
