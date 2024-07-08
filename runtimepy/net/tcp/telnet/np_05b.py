"""
A module implementing a Telnet interface for the NP-05B.
"""

# built-in
from argparse import Namespace
import asyncio
from enum import Enum
from typing import List, Optional, Union

# third-party
from vcorelib.python import StrToBool

# internal
from runtimepy.channel.environment.command import FieldOrChannel
from runtimepy.channel.environment.command.parser import ChannelCommand
from runtimepy.mixins.async_command import AsyncCommandProcessingMixin
from runtimepy.net.tcp.telnet import BasicTelnet


class Np05bStrings(Enum):
    """Command strings for the NP-05B."""

    SET_OUTLET = "$A3"

    # Requires polling to remain synchronized with device, 'reboot' is actually
    # a double toggle with a constant time in between (not that useful).
    # REBOOT = "$A4"

    OUTLET_STATUS = "$A5"
    ALL_OUTLETS = "$A7"

    OK = "$A0"
    FAIL = "$AF"

    @staticmethod
    def is_command(data: str) -> bool:
        """Determine if some string data is a command string."""
        return data.startswith("$A")


class Np05bConnection(BasicTelnet, AsyncCommandProcessingMixin):
    """
    A class implementing a communication interface with the NP-05B networked
    PDU.
    """

    # Connection settings.
    default_auto_restart = True

    # Defaults.
    num_ports = 5
    prompt = ">"

    # Typing for some instance members.
    prev_cmd: str
    chan_to_idx: dict[str, int]

    lock: asyncio.Lock

    def init(self) -> None:
        """Initialize this instance."""

        self.lock = asyncio.Lock()

        self.prev_cmd = ""
        self.outlets_on: List[Union[None, bool]] = [
            None for _ in range(self.num_ports)
        ]
        self.outlet_status_sem = asyncio.Semaphore(0)
        self.chan_to_idx = {}

        # Add runtime state.
        namespace = "outlet"
        with self.env.names_pushed(namespace):
            for idx in range(self.num_ports):
                one_idx = idx + 1
                chan = f"{one_idx}.on"
                self.env.namespace(chan)
                self.chan_to_idx[f"{namespace}.{chan}"] = one_idx
                self.env.bool_channel(
                    chan,
                    commandable=True,
                    default=False,
                    description=f"Current state of outlet {one_idx}.",
                )

        async def all_on(_: Namespace, __: Optional[FieldOrChannel]) -> None:
            """Handle an 'all_on' command."""
            await self.np05b_command(Np05bStrings.ALL_OUTLETS, "1")

        async def all_off(_: Namespace, __: Optional[FieldOrChannel]) -> None:
            """Handle an 'all_off' command."""
            await self.np05b_command(Np05bStrings.ALL_OUTLETS, "0")

        self._setup_async_commands(all_on, all_off)

    async def handle_command(
        self, args: Namespace, channel: Optional[FieldOrChannel]
    ) -> None:
        """Handle a command."""

        idx = self.chan_to_idx.get(args.channel)
        if idx is not None:
            curr = self.outlets_on[idx - 1]
            to_set = None

            # Handle toggle.
            if args.command == ChannelCommand.TOGGLE and curr is not None:
                to_set = not curr

            # Handle explicit value.
            elif args.extra:
                parsed = StrToBool.parse(args.extra[0])
                if parsed.valid:
                    to_set = parsed.result

            if to_set is not None:
                await self.set_outlet_state(idx, to_set)

    async def async_init(self) -> bool:
        """Ensure that initial statuses get set."""

        await self.request_outlet_status()
        return True

    def _send_np05b(self, message: Np05bStrings, *parts: str) -> None:
        """Send a specific message."""

        msg = " ".join([message.value, *parts])
        self.logger.debug("Sending: '%s'.", msg)
        self.send_text(msg + "\r\n")

    async def np05b_command(self, message: Np05bStrings, *parts: str) -> None:
        """Send a command then read outlet states."""

        async with self.lock:
            self._send_np05b(message, *parts)
            await asyncio.wait_for(self.request_outlet_status(), 5.0)

    async def request_outlet_status(self) -> None:
        """Request that the endpoint sends information about outlet status."""

        self._send_np05b(Np05bStrings.OUTLET_STATUS)

        # Wait for the device to respond.
        await self.outlet_status_sem.acquire()

    async def set_outlet_state(self, idx: int, state: bool) -> bool:
        """
        Set the state of an outlet on the PDU. Returns whether or not the state
        for the specified outlet index got set.
        """

        result = False
        real_idx = idx - 1

        if 0 <= real_idx <= self.num_ports:
            if self.outlets_on[real_idx] != state:
                await self.np05b_command(
                    Np05bStrings.SET_OUTLET, str(idx), "1" if state else "0"
                )

            result = self.outlets_on[real_idx] == state

        return result

    def process_response(
        self, command: Np05bStrings, command_data: str, response: str
    ) -> None:
        """Process a command response from the NP-05B."""

        parts = response.split(",")
        result = Np05bStrings(parts[0])

        if result is Np05bStrings.FAIL:
            self.logger.error(
                "Command %s ('%s') failed: %s.",
                command.name,
                command_data,
                parts,
            )
        else:
            assert result is Np05bStrings.OK
            self.logger.info(
                "Command %s ('%s') succeeded.", command.name, command_data
            )

        if command is Np05bStrings.OUTLET_STATUS:
            if result is Np05bStrings.OK:
                # Reverse the string because the output is sent in reverse
                # order.
                for idx, val in enumerate(parts[1][::-1]):
                    prev = self.outlets_on[idx]
                    curr = val == "1"

                    # Log any state changes.
                    if prev != curr:
                        self.logger.debug(
                            "Output %d changed: %s -> %s", idx + 1, prev, curr
                        )

                    self.outlets_on[idx] = curr
                    self.env.set(f"outlet.{idx + 1}.on", curr)

            # Signal that we got a response to outlet status.
            self.outlet_status_sem.release()

    async def process_text(self, data: str) -> bool:
        """Process a text frame."""

        line_stack = list(data.splitlines())

        while line_stack:
            line = line_stack.pop(0)

            # We can skip lines that don't mean anything.
            if not line or line == self.prompt:
                continue

            # The device's response strings can end up on the same line. Split
            # lines with multiple command markers in them and re-process them
            # on the next iterations.
            commands = line.split("$A")
            if len(commands) > 2:
                line_stack = [f"$A{x}" for x in commands[1:]] + line_stack
                continue

            if Np05bStrings.is_command(line):
                # The device echo's incoming commands, so if the current
                # and previous lines have command markers, we can process
                # this line as the response.
                if Np05bStrings.is_command(self.prev_cmd):
                    self.process_response(
                        Np05bStrings(self.prev_cmd[:3]),
                        self.prev_cmd[3:].strip(),
                        line,
                    )
                    self.prev_cmd = ""
                else:
                    self.prev_cmd = line

            # Log lines that aren't commands or responses.
            else:
                self.logger.info(line)

        return True
