"""
A module implementing a simple web application.
"""

# built-in
from pathlib import Path
from typing import Iterable, Optional

# third-party
from svgen.element import Element
from svgen.element.html import Html
from vcorelib.asyncio.cli import run_command
from vcorelib.logging import LoggerType
from vcorelib.paths import Pathlike, modified_after, normalize

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader
from runtimepy.net.server import RuntimepyServerConnection
from runtimepy.net.server.app.create import config_param
from runtimepy.net.server.app.elements import div
from runtimepy.net.server.app.files import append_kind
from runtimepy.net.server.html import HtmlApp


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


DEFAULT_APP = "hello_world"


async def build_app(
    app: Pathlike, paths: list[Path], logger: LoggerType, is_async: bool = True
) -> Element:
    """Build the application."""

    # Find the source file.
    app = normalize(app)
    source = search_paths(app, paths, {".c", ".cc"})
    assert source is not None, (app, paths)

    # Find a possible existing script file.
    script = app.with_suffix(".js")

    script_dest = source.parent.joinpath(script.name)

    # Run emcc.
    sources = [source]
    if not script_dest.is_file() or modified_after(script_dest, sources):
        await run_command(logger, "emcc", str(source), "-o", str(script_dest))

    # Manifest the script file in the application.
    elem = Element(tag="script", src=str(script), text="/* null */")
    if is_async:
        elem.booleans.add("async")
    return elem


def create(app: AppInfo, paths: list[Path]) -> HtmlApp:
    """Create a web-application handler."""

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
        document.body.children.append(
            await build_app(
                config_param(app, "wasm_app", "", strict=True),
                paths,
                app.logger,
            )
        )

        return document

    return main


async def setup(app: AppInfo) -> int:
    """Perform server application setup steps."""

    # Add WASM root directory.
    paths = RuntimepyServerConnection.class_paths
    paths.insert(0, config_param(app, "wasm_root", Path(), strict=True))

    # Set default application.
    RuntimepyServerConnection.default_app = create(
        app, list(normalize(x).resolve() for x in paths)
    )

    return 0
