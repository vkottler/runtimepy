"""
Test the 'net' module.
"""

# module under test
from runtimepy.net import IPv6Host, get_free_socket_name, normalize_host


def test_get_free_socket_name_basic():
    """Test that we can get the name of an available socket."""

    host = IPv6Host()
    assert str(host)
    assert get_free_socket_name(local=host)
    assert normalize_host(*host)
