"""
A module implementing interfaces for working with file contents.
"""

# built-in
from io import StringIO

# third-party
from svgen.element import Element
from vcorelib import DEFAULT_ENCODING
from vcorelib.io import IndentedFileWriter
from vcorelib.paths import find_file

# internal
from runtimepy import PKG_NAME


def write_found_file(writer: IndentedFileWriter, *args, **kwargs) -> None:
    """Write a file's contents to the file-writer's stream."""

    entry = find_file(*args, **kwargs)
    assert entry is not None
    with entry.open(encoding=DEFAULT_ENCODING) as path_fd:
        for line in path_fd:
            writer.write(line)


def set_text_to_file(element: Element, *args, **kwargs) -> None:
    """Set an element's text to the contents of a file."""

    with StringIO() as stream:
        write_found_file(
            IndentedFileWriter(stream, per_indent=2), *args, **kwargs
        )
        element.text = stream.getvalue()


def kind_url(kind: str, name: str, package: str = PKG_NAME) -> str:
    """Return a URL to find a package resource."""
    return f"package://{package}/{kind}/{name}.{kind}"


def set_text_to_kind(
    element: Element, kind: str, name: str, package: str = PKG_NAME
) -> None:
    """Set text to HTML-file contents at a predictable path."""

    set_text_to_file(element, kind_url(kind, name, package=package))


def append_kind(
    element: Element,
    *names: str,
    package: str = PKG_NAME,
    kind: str = "js",
    tag: str = "script",
) -> Element:
    """Append a new script element."""

    elem = Element(tag=tag)

    with StringIO() as stream:
        writer = IndentedFileWriter(stream, per_indent=2)
        for name in names:
            write_found_file(writer, kind_url(kind, name, package=package))
        elem.text = stream.getvalue()

    element.children.append(elem)
    return elem
