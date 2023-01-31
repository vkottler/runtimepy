"""
Test the 'net' module.
"""

# module under test
from runtimepy.net import get_free_socket_name


def test_get_free_socket_name_basic():
    """Test that we can get the name of an available socket."""

    assert get_free_socket_name()
