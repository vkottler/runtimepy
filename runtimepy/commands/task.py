"""
An entry-point for the 'task' command.
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


def config_data(args: _Namespace) -> dict[str, Any]:
    """Get configuration data for the 'task' command."""

    return {
        "includes": [FACTORIES],
        "tasks": [
            {
                "name": args.factory,
                "factory": args.factory,
                "period_s": 1.0 / args.rate,
            }
        ],
    }


def task_cmd(args: _Namespace) -> int:
    """Execute the task command."""

    return cmd_with_jit(arbiter_cmd, args, config_data(args))


def add_task_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add task-command arguments to its parser."""

    with arbiter_args(parser, nargs="*"):
        parser.add_argument(
            "-r",
            "--rate",
            default=10,
            type=float,
            help=(
                "rate (in Hz) that the task should run "
                "(default: %(default)s)"
            ),
        )
        parser.add_argument(
            "factory", help="name of task factory to create task with"
        )

    return task_cmd
