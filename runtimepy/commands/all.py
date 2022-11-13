# =====================================
# generator=datazen
# version=3.1.0
# hash=fd5cef0b65ab393b390edc69e1c670f7
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
from runtimepy.commands.tui import add_tui_cmd


def commands() -> _List[_Tuple[str, str, _CommandRegister]]:
    """Get this package's commands."""

    return [
        (
            "tui",
            "run a terminal interface for the channel environment",
            add_tui_cmd,
        ),
        ("noop", "command stub (does nothing)", lambda _: lambda _: 0),
    ]
