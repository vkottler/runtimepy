"""
A module implementing a channel-environment command argument parser wrapper.
"""

# built-in
from argparse import ArgumentParser
from enum import StrEnum
from typing import Any


class ChannelCommand(StrEnum):
    """An enumeration for all channel command options."""

    SET = "set"
    TOGGLE = "toggle"
    GET = "get"
    CUSTOM = "custom"


class CommandParser(ArgumentParser):
    """An argument parser wrapper."""

    data: dict[str, Any]

    def error(self, message: str):
        """Pass error message to error handling."""
        self.data["error_message"] = message

    def exit(self, status: int = 0, message: str = None):
        """Override exit behavior."""

        del status

        if message:
            curr = self.data.get("error_message")
            curr = curr + f" [{message}]" if curr else message
            self.data["error_message"] = curr

    def initialize(self) -> None:
        """Initialize this command parser."""

        self.add_argument(
            "command",
            type=ChannelCommand,
            choices=set(ChannelCommand),
            help="command to run",
        )

        self.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="operate on a channel even if it's not commandable",
        )
        self.add_argument(
            "-r",
            "--remote",
            action="store_true",
            help="attempt to send a remote command",
        )
        self.add_argument(
            "-e",
            "--env",
            default="default",
            help="channel environment to run command against",
        )

        self.add_argument(
            "channel", type=str, help="channel to perform action on"
        )

        self.add_argument("extra", nargs="*")
