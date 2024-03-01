"""
Test the 'net.server.app.elements' module.
"""

# module under test
from runtimepy.net.server.app.elements import kind


def test_html_kind_basic():
    """Test basic HTML-loading scenarios."""

    assert kind("example")
