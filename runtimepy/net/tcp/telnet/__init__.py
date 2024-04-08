"""
A module implementing a basic telnet (RFC 854) connection interface.
"""

# built-in
from abc import abstractmethod as _abstractmethod
from contextlib import ExitStack as _ExitStack
from io import BytesIO as _BytesIO
from typing import BinaryIO as _BinaryIO

# third-party
from vcorelib import DEFAULT_ENCODING

# internal
from runtimepy.net.tcp.connection import TcpConnection as _TcpConnection
from runtimepy.net.tcp.telnet.codes import (
    CARRIAGE_RETURN,
    NEWLINE,
    TelnetCode,
    TelnetNvt,
)

__all__ = [
    "TelnetCode",
    "TelnetNvt",
    "Telnet",
    "BasicTelnet",
    "NEWLINE",
    "CARRIAGE_RETURN",
]


class Telnet(_TcpConnection):
    """A class implementing a basic telnet interface."""

    log_alias = "TELNET"

    async def process_telnet_message(self, data: bytes) -> bool:
        """By default, treat all incoming data bytes as text."""
        return await self.process_text(data.decode(encoding=DEFAULT_ENCODING))

    @_abstractmethod
    async def process_command(self, code: TelnetCode) -> None:
        """Process a telnet command."""

    def send_command(self, code: TelnetCode) -> None:
        """Send a telnet command."""
        self.send_binary(bytes([TelnetCode.IAC, code]))

    def send_option(self, option: TelnetCode, code: int) -> None:
        """
        Send a telnet option sequence. if the 'SB' is the desired code, the
        additional data can be sent using the 'send_binary' method directly.
        """
        assert TelnetCode.is_option_code(option)
        self.send_binary(bytes([TelnetCode.IAC, option, code]))

    @_abstractmethod
    async def handle_nvt(self, action: TelnetNvt) -> None:
        """Handle a signal for the network virtual-terminal."""

    @_abstractmethod
    async def process_option(
        self, code: TelnetCode, option: int, stream: _BinaryIO
    ) -> None:
        """Process a telnet option."""

    async def process_binary(self, data: bytes) -> bool:
        """Process a binary frame."""

        result = True

        last_val = 0
        val = 0

        # These two conditions are used to form a simple state machine.
        processing_option = False
        processing_command = False

        with _ExitStack() as stack:
            text = stack.enter_context(_BytesIO())
            stream = stack.enter_context(_BytesIO(data))

            while True:
                data = stream.read(1)
                if len(data) == 0:
                    break

                last_val = val
                val = data[0]

                if processing_option:
                    await self.process_option(
                        TelnetCode(last_val), val, stream
                    )
                    processing_option = False

                elif processing_command:
                    if TelnetCode.is_option_code(val):
                        processing_option = True
                    else:
                        # If 'IAC' appears twice in a row, it's being
                        # escaped.
                        if val == TelnetCode.IAC:
                            text.write(data)
                        else:
                            await self.process_command(TelnetCode(val))

                    processing_command = False

                elif val == TelnetCode.IAC:
                    processing_command = True

                elif TelnetNvt.is_nvt(val):
                    nvt = TelnetNvt(val)
                    if not nvt.to_stream(text):
                        await self.handle_nvt(TelnetNvt(val))

                # Forward byte to the data stream.
                else:
                    text.write(data)

            # Process the message that remains as data.
            if text.tell() > 0:
                result = await self.process_telnet_message(text.getvalue())

        return result


class BasicTelnet(Telnet):
    """A simple telnet implementation."""

    async def process_text(self, data: str) -> bool:
        """Process a text frame."""

        self.logger.info("Text: '%s'.", data)
        return True

    async def process_command(self, code: TelnetCode) -> None:
        """Process a telnet command."""
        self.logger.info("Command: %s (%d).", code, code)

        if code is TelnetCode.IP:
            self.disable("Interrupt Process")

    async def handle_nvt(self, action: TelnetNvt) -> None:
        """Handle a signal for the network virtual-terminal."""

        if action is not TelnetNvt.NUL:
            self.logger.info("NVT signal: %s (%d).", action, action)

    async def process_option(
        self, code: TelnetCode, option: int, _: _BinaryIO
    ) -> None:
        """Process a telnet option."""
        self.logger.info("Option: %s (%d), %d", code, code, option)
