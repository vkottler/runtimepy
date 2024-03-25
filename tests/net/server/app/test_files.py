"""
Test the 'net.server.app.files' module.
"""

# third-party
from svgen.element import Element

# module under test
from runtimepy import PKG_NAME
from runtimepy.net.server.app.files import kind_url, set_text_to_file


def test_set_text_to_file_basic():
    """Test basic functionality of this method."""

    assert kind_url("js", "test", subdir="subdir")

    assert set_text_to_file(Element(), f"package://{PKG_NAME}/js/main.js")
