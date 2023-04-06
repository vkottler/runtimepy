"""
Code enumerations relevant to the telnet (RFC 854) protocol.
"""

# built-in
from enum import IntEnum as _IntEnum
from typing import BinaryIO as _BinaryIO


class TelnetCode(_IntEnum):
    """An enumeration of byte values important to the telnet protocol."""

    # End of subnegotiation parameters.
    SE = 240

    # No operation.
    NOP = 241

    # The data stream portion of a Synch. This should always be accompanied
    # by a TCP Urgent notification.
    DATA_MARK = 242

    # NVT character BRK.
    BREAK = 243

    # The function IP.
    IP = 244

    # The function AO.
    AO = 245

    # The function AYT.
    AYT = 246

    # The function EC.
    EC = 247

    # The function EL.
    EL = 248

    # The GA signal.
    GA = 249

    # Indicates that what follows is subnegotiation of the indicated
    # option.
    SB = 250

    # (option code) Indicates the desire to begin performing, or confirmation
    # that you are now performing, the indicated option.
    WILL = 251

    # (option code) Indicates the refusal to perform, or continue performing,
    # the indicated option.
    WONT = 252

    # (option code) Indicates the request that the other party perform, or
    # confirmation that you are expecting the other party to perform, the
    # indicated option.
    DO = 253

    # (option code) Indicates the demand that the other party stop performing,
    # or confirmation that you are no longer expecting the other party
    # to perform, the indicated option.
    DONT = 254

    # Data Byte 255.
    IAC = 255

    @staticmethod
    def is_option_code(val: int) -> bool:
        """Determine if the integer value is an option code."""
        return TelnetCode.WILL <= val <= TelnetCode.DONT


class TelnetNvt(_IntEnum):
    """Telnet data relevant to the NVT printer and keyboard."""

    # NULL: No Operation
    NUL = 0

    # Line Feed: Moves the printer to the next print line, keeping the
    # same horizontal position.
    LF = 10

    # Carriage Return: Moves the printer to the left margin of the current
    # line.
    CR = 13

    # BELL: Produces an audible or visible signal (which does NOT move the
    # print head).
    BEL = 7

    # Back Space: Moves the print head one character position towards the left
    # margin.
    BS = 8

    # Horizontal Tab: Moves the printer to the next horizontal tab stop.
    # It remains unspecified how either party determines or establishes where
    # such tab stops are located.
    HT = 9

    # Vertical Tab: Moves the printer to the next vertical tab stop. It
    # remains unspecified how either party determines or establishes where such
    # tab stops are located.
    VT = 11

    # Moves the printer to the top of the next page, keeping the same
    # horizontal position.
    FF = 12

    def to_stream(self, stream: _BinaryIO) -> bool:
        """
        Add text to the provided stream based on this NVT instance. Return
        whether or not any data was written to the stream.
        """

        result = False

        if (
            self is TelnetNvt.CR
            or self is TelnetNvt.LF
            or self is TelnetNvt.HT
        ):
            stream.write(bytes([self]))
            result = True

        return result

    @staticmethod
    def is_nvt(val: int) -> bool:
        """Determine if a byte value is an NVT printer or keyboard code."""
        return val == 0 or 7 <= val <= 13


NEWLINE = bytes([TelnetNvt.CR, TelnetNvt.LF])
CARRIAGE_RETURN = bytes([TelnetNvt.CR, TelnetNvt.NUL])
