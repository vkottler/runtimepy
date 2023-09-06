# =====================================
# generator=datazen
# version=3.1.3
# hash=9e87f6454df00f68a60186c6e98c7f81
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
            "tui",
            "run a terminal interface for the channel environment",
            add_tui_cmd,
        ),
        ("noop", "command stub (does nothing)", lambda _: lambda _: 0),
    ]
