"""
An entry-point for the 'server' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from typing import Any

# third-party
from vcorelib.args import CommandFunction as _CommandFunction

# internal
from runtimepy.commands.arbiter import arbiter_cmd
from runtimepy.commands.common import FACTORIES, arbiter_args, cmd_with_jit


def port_name(args: _Namespace, port: str = "port") -> str:
    """Get the name for a connection factory's port."""
    return f"{args.factory}_{'udp' if args.udp else 'tcp'}_{port}"


def server_data(args: _Namespace) -> dict[str, Any]:
    """Get server data based on command-line arguments."""

    return {
        "factory": args.factory,
        "kwargs": {"port": f"${port_name(args)}", "host": args.host},
    }


def is_websocket(args: _Namespace) -> bool:
    """Determine if the specified factory uses WebSocket or not."""
    return "websocket" in args.factory.lower()


def client_data(args: _Namespace) -> dict[str, Any]:
    """Get client data based on command-line arguments."""

    port = f"${port_name(args)}"

    arg_list: list[Any] = []
    kwargs: dict[str, Any] = {}

    if is_websocket(args):
        arg_list.append(f"ws://localhost:{port}")
    elif not args.udp:
        kwargs["host"] = "localhost"
        kwargs["port"] = port
    else:
        kwargs["remote_addr"] = ["localhost", port]

    result = {
        "name": port_name(args, port="client"),
        "defer": True,
        "factory": args.factory,
    }
    if arg_list:
        result["args"] = arg_list
    if kwargs:
        result["kwargs"] = kwargs

    return result


def config_data(args: _Namespace) -> dict[str, Any]:
    """Get configuration data for the 'server' command."""

    servers = []
    clients = []

    if not args.udp:
        servers.append(server_data(args))
    else:
        clients.append(
            {
                "name": port_name(args, port="server"),
                "factory": args.factory,
                "kwargs": {"local_addr": ["0.0.0.0", f"${port_name(args)}"]},
            }
        )

    # Add a loopback connection if specified.
    if args.loopback:
        clients.append(client_data(args))

    return {
        "includes": [FACTORIES] + args.configs,
        "clients": clients,
        "servers": servers,
        "ports": [
            {
                "name": port_name(args),
                "port": args.port,
                "type": "udp" if args.udp else "tcp",
            }
        ],
    }


def server_cmd(args: _Namespace) -> int:
    """Execute the server command."""

    return cmd_with_jit(arbiter_cmd, args, config_data(args))


def add_server_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add server-command arguments to its parser."""

    with arbiter_args(parser, nargs="*"):
        parser.add_argument(
            "--host",
            default="0.0.0.0",
            help="host address to listen on (default: '%(default)s')",
        )
        parser.add_argument(
            "-p",
            "--port",
            default=0,
            type=int,
            help="port to listen on (default: %(default)s)",
        )
        parser.add_argument(
            "-u",
            "--udp",
            action="store_true",
            help="whether or not this is a UDP-based server "
            "(otherwise it must be a TCP-based server)",
        )
        parser.add_argument(
            "-l",
            "--loopback",
            action="store_true",
            help="if true a client of the same connection type is added",
        )
        parser.add_argument(
            "factory", help="name of connection factory to create server for"
        )

    return server_cmd
