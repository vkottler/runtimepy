"""
An entry-point for the 'server' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from typing import Any, Dict

# third-party
from vcorelib.args import CommandFunction as _CommandFunction
from vcorelib.io import ARBITER
from vcorelib.paths.context import tempfile

# internal
from runtimepy import PKG_NAME
from runtimepy.commands.arbiter import arbiter_cmd
from runtimepy.commands.common import arbiter_args


def server_data(args: _Namespace) -> Dict[str, Any]:
    """Get server data based on command-line arguments."""

    return {
        "factory": args.factory,
        "kwargs": {"port": args.port, "host": args.host},
    }


def server_cmd(args: _Namespace) -> int:
    """Execute the server command."""

    with tempfile(suffix=".yaml") as temp_config:
        ARBITER.encode(
            temp_config,
            {
                "includes": [f"package://{PKG_NAME}/factories.yaml"],
                "servers": [server_data(args)],  # type: ignore
                "app": ["runtimepy.net.apps.wait_for_stop"],
            },
        )

        # Ensure injected data is loaded.
        args.configs.append(str(temp_config))
        return arbiter_cmd(args)


def add_server_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add server-command arguments to its parser."""

    with arbiter_args(parser, nargs="*"):
        parser.add_argument(
            "--host",
            default="0.0.0.0",
            help="host address to listen on (default: %(default)s)",
        )
        parser.add_argument(
            "-p",
            "--port",
            default=0,
            type=int,
            help="port to listen on (default: %(default)s)",
        )
        parser.add_argument(
            "factory", help="name of connection factory to create server for"
        )

    return server_cmd
