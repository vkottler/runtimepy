"""
Test the 'runtimepy.task.basic.manager' module.
"""

# module under test
from runtimepy.task import PeriodicTaskManager


def test_periodic_task_manager_basic():
    """Test basic interactions with a periodic-task manager."""

    manager = PeriodicTaskManager()
    assert manager
