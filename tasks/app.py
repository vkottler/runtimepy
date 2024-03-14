"""
A module implementing a simple web application.
"""

# built-in
from pathlib import Path
from typing import Iterable, Optional

# third-party
from svgen.element import Element
from svgen.element.html import Html
from vcorelib.paths import normalize

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader
from runtimepy.net.server import RuntimepyServerConnection
from runtimepy.net.server.app.elements import div
from runtimepy.net.server.app.files import append_kind
from runtimepy.net.server.html import HtmlApp
from tasks.compile_commands import EmscriptenBuilder


def search_paths(
    path: Path, paths: list[Path], suffixes: Iterable[str]
) -> Optional[Path]:
    """Search for a file given a list of paths."""

    result = None
    candidate = None
    for search in paths:
        if result is not None:
            break

        for suffix in suffixes:
            candidate = search.joinpath(path).with_suffix(suffix)
            if candidate.is_file():
                result = candidate
                break

    return result


async def build_app(
    app: AppInfo, paths: list[Path], is_async: bool = True
) -> Element:
    """Build the application."""

    # Find the source file.
    app_path = normalize(app.config_param("wasm_app", "", strict=True))
    source = search_paths(app_path, paths, {".c", ".cc"})
    assert source is not None, (app_path, paths)

    # Find a possible existing script file.
    script = app_path.with_suffix(".js")

    # Build if necessary. Should we get the root directory a different way?
    builder = EmscriptenBuilder(app.logger, Path())
    await builder.handle(source, source.parent.joinpath(script.name))

    # Manifest the script file in the application.
    elem = Element(tag="script", src=str(script), text="/* null */")
    if is_async:
        elem.booleans.add("async")
    return elem


def create(app: AppInfo) -> HtmlApp:
    """Create a web-application handler."""

    # Add WASM root directory.
    paths = RuntimepyServerConnection.class_paths
    paths.insert(0, app.wasm_root)

    paths = list(normalize(x).resolve() for x in paths)

    async def main(
        document: Html,
        request: RequestHeader,
        response: ResponseHeader,
        request_data: Optional[bytes],
    ) -> Html:
        """A simple 'Hello, world!' application."""

        # Not currently used.
        del request
        del response
        del request_data

        # Create the application.
        append_kind(document.head, "main", kind="css", tag="style")

        # Remove at some point.
        div(text="Hello, world!", parent=document.body)

        # Add WebAssembly application.
        document.body.children.append(await build_app(app, paths))

        return document

    return main


async def setup(app: AppInfo) -> int:
    """Perform server application setup steps."""

    # Set default application.
    RuntimepyServerConnection.default_app = create(app)
    return 0
