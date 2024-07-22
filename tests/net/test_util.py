"""
Test the 'net.util' module.
"""

# module under test
from runtimepy.net.util import IPv4Host, IPv6Host


def test_ip_hosts():
    """Test basic instantiations of IP host instances."""

    ipv4 = IPv4Host("127.0.0.1", 0)
    assert ipv4.hostname
    assert ipv4.address
    assert str(ipv4)
    assert hash(ipv4)

    ipv6 = IPv6Host("::1", 0)
    assert ipv6.hostname
    assert ipv6.address
    assert str(ipv6)
    assert hash(ipv6)
