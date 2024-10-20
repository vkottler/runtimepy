"""
A module implementing interfaces for working with file contents.
"""

# built-in
from io import StringIO

# third-party
from svgen.element import Element
from vcorelib.io import IndentedFileWriter

# internal
from runtimepy import PKG_NAME
from runtimepy.net.html import kind_url, write_found_file


def set_text_to_file(element: Element, *args, **kwargs) -> bool:
    """Set an element's text to the contents of a file."""

    with StringIO() as stream:
        result = write_found_file(
            IndentedFileWriter(stream, per_indent=2), *args, **kwargs
        )
        if result:
            element.text = stream.getvalue()

    return result


def set_text_to_kind(
    element: Element,
    kind: str,
    name: str,
    package: str = PKG_NAME,
    subdir: str = None,
) -> bool:
    """Set text to HTML-file contents at a predictable path."""

    return set_text_to_file(
        element, kind_url(kind, name, subdir=subdir, package=package)
    )
