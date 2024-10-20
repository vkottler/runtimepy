"""
A module implementing HTML-related interfaces.
"""

# built-in
from io import StringIO
from typing import Optional

# third-party
from svgen.element import Element
from svgen.element.html import Html, div
from vcorelib import DEFAULT_ENCODING
from vcorelib.io import IndentedFileWriter
from vcorelib.paths import find_file

# internal
from runtimepy import PKG_NAME
from runtimepy.net.html.bootstrap import (
    add_bootstrap_css,
    add_bootstrap_js,
    icon_str,
)
from runtimepy.net.html.bootstrap.elements import (
    bootstrap_button,
    centered_markdown,
)


def create_app_shell(parent: Element, **kwargs) -> tuple[Element, Element]:
    """Create a bootstrap-based application shell."""

    container = div(parent=parent, **kwargs)
    container.add_class("d-flex", "align-items-start", "bg-body")

    # Dark theme.
    container["data-bs-theme"] = "dark"

    # Buttons.
    button_column = div(parent=container)
    button_column.add_class("d-flex", "flex-column", "h-100", "bg-dark-subtle")

    # Dark/light theme switch button.
    bootstrap_button(
        icon_str("lightbulb"),
        tooltip=" Toggle light/dark.",
        id="theme-button",
        parent=button_column,
    )

    return container, button_column


def markdown_page(parent: Element, markdown: str, **kwargs) -> None:
    """Compose a landing page."""

    container = centered_markdown(
        create_app_shell(parent, **kwargs)[0], markdown, "h-100", "text-body"
    )
    container.add_class("overflow-y-auto")


def common_css(document: Html) -> None:
    """Add common CSS to an HTML document."""

    append_kind(document.head, "font", kind="css", tag="style")
    add_bootstrap_css(document.head)
    append_kind(
        document.head, "main", "bootstrap_extra", kind="css", tag="style"
    )


def full_markdown_page(document: Html, markdown: str) -> None:
    """Render a full markdown HTML app."""

    common_css(document)
    markdown_page(document.body, markdown, id=PKG_NAME)

    # JavaScript.
    append_kind(document.body, "markdown_page")
    add_bootstrap_js(document.body)


def handle_worker(writer: IndentedFileWriter) -> int:
    """Boilerplate contents for worker thread block."""

    # Not currently used.
    # return write_found_file(
    #     writer, kind_url("js", "webgl-debug", subdir="third-party")
    # )
    del writer

    return 0


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


def kind_url(
    kind: str, name: str, subdir: str = None, package: str = PKG_NAME
) -> str:
    """Return a URL to find a package resource."""

    path = kind

    if subdir is not None:
        path += "/" + subdir

    path += f"/{name}"

    return f"package://{package}/{path}.{kind}"


WORKER_TYPE = "text/js-worker"


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

        if worker:
            found_count += handle_worker(writer)

        if found_count:
            elem.text = stream.getvalue()

    if found_count:
        element.children.append(elem)

    if worker:
        elem["type"] = WORKER_TYPE

    return elem if found_count else None
