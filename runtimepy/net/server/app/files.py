"""
A module implementing interfaces for working with file contents.
"""

# built-in
from io import StringIO
from typing import Optional

# third-party
from svgen.element import Element
from vcorelib import DEFAULT_ENCODING
from vcorelib.io import IndentedFileWriter
from vcorelib.paths import find_file

# internal
from runtimepy import PKG_NAME


def write_found_file(writer: IndentedFileWriter, *args, **kwargs) -> bool:
    """Write a file's contents to the file-writer's stream."""

    result = False

    entry = find_file(*args, **kwargs)
    if entry is not None:
        with entry.open(encoding=DEFAULT_ENCODING) as path_fd:
            for line in path_fd:
                writer.write(line)

        result = True

    return result


def set_text_to_file(element: Element, *args, **kwargs) -> bool:
    """Set an element's text to the contents of a file."""

    with StringIO() as stream:
        result = write_found_file(
            IndentedFileWriter(stream, per_indent=2), *args, **kwargs
        )
        if result:
            element.text = stream.getvalue()

    return result


def kind_url(
    kind: str, name: str, subdir: str = None, package: str = PKG_NAME
) -> str:
    """Return a URL to find a package resource."""

    path = kind

    if subdir is not None:
        path += "/" + subdir

    path += f"/{name}"

    return f"package://{package}/{path}.{kind}"


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


WORKER_TYPE = "text/js-worker"


def handle_worker(writer: IndentedFileWriter) -> bool:
    """Boilerplate contents for worker thread block."""

    return write_found_file(
        writer, kind_url("js", "webgl-debug", subdir="third-party")
    )


def append_kind(
    element: Element,
    *names: str,
    package: str = PKG_NAME,
    kind: str = "js",
    tag: str = "script",
    subdir: str = None,
    worker: bool = False,
) -> Optional[Element]:
    """Append a new script element."""

    elem = Element(tag=tag, allow_no_end_tag=False)

    with StringIO() as stream:
        writer = IndentedFileWriter(stream, per_indent=2)
        found_count = 0
        for name in names:
            if write_found_file(
                writer, kind_url(kind, name, subdir=subdir, package=package)
            ):
                found_count += 1

        if worker and handle_worker(writer):
            found_count += 1

        if found_count:
            elem.text = stream.getvalue()

    if found_count:
        element.children.append(elem)

    if worker:
        elem["type"] = WORKER_TYPE

    return elem if found_count else None
