"""
An entry-point for the 'task' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from typing import Any, Dict

# third-party
from vcorelib.args import CommandFunction as _CommandFunction

# internal
from runtimepy import PKG_NAME
from runtimepy.commands.arbiter import arbiter_cmd
from runtimepy.commands.common import arbiter_args, cmd_with_jit


def config_data(args: _Namespace) -> Dict[str, Any]:
    """Get configuration data for the 'task' command."""

    # handle period

    return {
        "includes": [f"package://{PKG_NAME}/factories.yaml"],
        "tasks": [{"name": args.factory, "factory": args.factory}],
    }


def task_cmd(args: _Namespace) -> int:
    """Execute the task command."""

    return cmd_with_jit(arbiter_cmd, args, config_data(args))


def add_task_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add task-command arguments to its parser."""

    with arbiter_args(parser, nargs="*"):
        parser.add_argument(
            "factory", help="name of task factory to create task with"
        )

        # period cli arg

    return task_cmd
