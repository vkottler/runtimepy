"""
Test that we can load test resources.
"""

# internal
from tests.resources import resource


def test_resources_basic():
    """Test that we can locate test data."""

    assert resource("test.txt").is_file()
    assert resource("test.txt", valid=False).is_file()
