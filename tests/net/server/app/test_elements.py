"""
Test the 'net.server.app.elements' module.
"""

# module under test
from runtimepy.net.server.app.elements import kind
from runtimepy.net.server.app.pyodide import add_pyodide_js


def test_html_kind_basic():
    """Test basic HTML-loading scenarios."""

    elem = kind("example")
    assert elem

    assert add_pyodide_js(elem)
