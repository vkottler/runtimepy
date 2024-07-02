"""
A module implementing tftp enums and other protocol minutia interfaces.
"""

# built-in
from io import BytesIO
from typing import BinaryIO

# internal
from runtimepy.enum.registry import RuntimeIntEnum


class TftpOpCode(RuntimeIntEnum):
    """A runtime enumeration for tftp op codes."""

    # Not an actual code.
    INVALID = 0

    RRQ = 1
    WRQ = 2
    DATA = 3
    ACK = 4
    ERROR = 5


class TftpErrorCode(RuntimeIntEnum):
    """A runtime enumeration for tftp error codes."""

    # Not defined, see error message (if any).
    UNKNOWN = 0

    # File not found.
    FILE_NOT_FOUND = 1

    # Access violation.
    ACCESS_VIOLATION = 2

    # Disk full or allocation exceeded.
    DISK_FULL = 3

    # Illegal TFTP operation.
    ILLEGAL_OPERATION = 4

    # Unknown transfer ID.
    UNKNOWN_ID = 5

    # File already exists.
    FILE_EXISTS = 6

    # No such user.
    NO_USER = 7

    # RFC 2347.
    OPTION_NEGOTIATION = 8


def parse_filename_mode(stream: BinaryIO) -> tuple[str, str]:
    """Parse two null-terminated strings from the provided stream."""

    result = stream.read().split(bytes(1))
    return result[0].decode(), result[1].decode()


DEFAULT_MODE = "octet"


def encode_filename_mode(filename: str, mode: str = DEFAULT_MODE) -> bytes:
    """Encode filename and mode for a tftp message."""

    with BytesIO() as stream:
        # Encode message.
        stream.write(filename.encode())
        stream.write(b"\x00")
        stream.write(mode.encode())
        stream.write(b"\x00")

        result = stream.getvalue()

    return result
