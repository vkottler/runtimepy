# =====================================
# generator=datazen
# version=3.2.0
# hash=1814b7f7fae3556a0dbeec37141e4182
# =====================================

"""
A module aggregating package commands.
"""

# built-in
from typing import List as _List
from typing import Tuple as _Tuple

# third-party
from vcorelib.args import CommandRegister as _CommandRegister

# internal
from runtimepy.commands.arbiter import add_arbiter_cmd
from runtimepy.commands.mtu import add_mtu_cmd
from runtimepy.commands.server import add_server_cmd
from runtimepy.commands.task import add_task_cmd
from runtimepy.commands.tftp import add_tftp_cmd
from runtimepy.commands.tui import add_tui_cmd


def commands() -> _List[_Tuple[str, str, _CommandRegister]]:
    """Get this package's commands."""

    return [
        (
            "arbiter",
            "run a connection-arbiter application from a config",
            add_arbiter_cmd,
        ),
        (
            "mtu",
            "probe for MTU size to some endpoint",
            add_mtu_cmd,
        ),
        (
            "server",
            "run a server for a specific connection factory",
            add_server_cmd,
        ),
        (
            "task",
            "run a task from a specific task factory",
            add_task_cmd,
        ),
        (
            "tftp",
            "perform a tftp interaction",
            add_tftp_cmd,
        ),
        (
            "tui",
            "run a terminal interface for the channel environment",
            add_tui_cmd,
        ),
        ("noop", "command stub (does nothing)", lambda _: lambda _: 0),
    ]
