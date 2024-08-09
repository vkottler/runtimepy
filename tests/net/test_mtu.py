"""
Test the 'net.mtu' module.
"""

# module under test
from runtimepy.net.mtu import discover_mtu
from runtimepy.net.util import IPv6Host, normalize_host


def test_ipv4_mtu_discovery() -> None:
    """Test that we can discover maximum transmission units."""

    assert discover_mtu("localhost", 80) > 0
    assert (
        discover_mtu("::1", 80, 0, 0, local=normalize_host(default=IPv6Host))
        > 0
    )
    assert discover_mtu("localhost", 80, probe_size=2**16) > 0