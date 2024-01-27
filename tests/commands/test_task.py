"""
Test the 'commands.task' module.
"""

# module under test
from runtimepy.entry import main as runtimepy_main

# internal
from tests.resources import base_args


def test_task_command_basic():
    """Test basic usages of the 'task' command."""

    base = base_args("task")
    assert runtimepy_main(base + ["sinusoid"]) == 0
