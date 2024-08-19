"""
A module implementing a message framing interface for serializables.
"""

# built-in
from typing import Optional

# third-party
from vcorelib.logging import LoggerType

# internal
from runtimepy.primitives.serializable.base import Serializable


class SerializableFramer:
    """A class implementing a serializable message framer."""

    elements: int
    raw: bytes

    def __init__(self, instance: Serializable, mtu: int) -> None:
        """Initiaize this instance."""

        self.instance = instance
        self.set_mtu(mtu)

    def set_mtu(
        self, mtu: int, logger: LoggerType = None, protocol_overhead: int = 0
    ) -> int:
        """Set a new maximum transmission unit for this framer."""

        raw_length = self.instance.length()
        assert raw_length > 0

        self.length = (mtu - protocol_overhead) // raw_length
        assert self.length > 0

        self.reset()

        if logger is not None:
            logger.info(
                "Set MTU to %d (%d %d-byte elements, %d bytes overhead).",
                mtu - protocol_overhead,
                self.length,
                raw_length,
                protocol_overhead,
            )

        return self.length

    def reset(self) -> None:
        """Reset this framer's state"""

        self.elements = 0
        self.raw = bytes()

    def capture(
        self, sample: bool = True, flush: bool = False
    ) -> Optional[bytes]:
        """
        Optionally sample this struct and attempt to resolve a full or flushed
        frame.
        """

        if sample:
            self.raw += bytes(self.instance)
            self.elements += 1

        result = None
        if self.raw and (flush or self.elements == self.length):
            result = self.raw
            self.reset()
        return result
