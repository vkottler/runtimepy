"""
A module implementing some basic HTML element interfaces.
"""

# third-party
from svgen.element import Element

# internal
from runtimepy.net.server.app.files import set_text_to_kind


def div(
    tag: str = "div",
    parent: Element = None,
    allow_no_end_tag: bool = False,
    **kwargs,
) -> Element:
    """Get a new 'div' element."""

    result = Element(tag=tag, allow_no_end_tag=allow_no_end_tag, **kwargs)

    if parent is not None:
        parent.children.append(result)

    return result


def kind(
    name: str, tag: str = "div", parent: Element = None, **kwargs
) -> Element:
    """Get an element populated with content from a file."""

    result = div(tag=tag, parent=parent, **kwargs)
    set_text_to_kind(result, "html", name)
    return result
