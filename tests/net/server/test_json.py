"""
Test the 'net.server.json' module.
"""

# module under test
from runtimepy.net.server.json import traverse_dict


def test_traverse_dict_basic():
    """Test basic dict-traversing scenarios."""

    src = {"a": lambda: {"a": 1, "b": 2, "c": 3}}

    assert traverse_dict(src, "", "a") == {"a": 1, "b": 2, "c": 3}
    assert traverse_dict(src, "a", "b") == 2
