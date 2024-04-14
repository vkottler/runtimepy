"""
A module implementing some basic HTML element interfaces.
"""

# third-party
from svgen.element import Element
from svgen.element.html import div

# internal
from runtimepy.net.server.app.files import set_text_to_kind


def kind(name: str, parent: Element = None, **kwargs) -> Element:
    """Get an element populated with content from a file."""

    result = div(parent=parent, **kwargs)
    set_text_to_kind(result, "html", name)
    return result
