"""
Test the 'task' module.
"""

# module under test
from runtimepy.task import rate_str


def test_rate_str_basic():
    """Test that we create the correct rate strings."""

    assert rate_str(1.0) == "1 Hz (1s)"
    assert rate_str(0.001) == "1000 Hz (1ms)"
