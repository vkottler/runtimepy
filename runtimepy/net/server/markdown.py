"""
A module implementing web server markdown interfaces.
"""

# built-in
from io import StringIO
from pathlib import Path
from typing import Iterable, cast

# third-party
from vcorelib.io.file_writer import IndentedFileWriter
from vcorelib.paths import rel

LOGO_MARKDOWN = (
    "[![logo](https://libre-embedded.com/static/"
    "png/chip-circle-bootstrap/128x128.png)](https://libre-embedded.com)"
)


def markdown_for_dir(
    path: Path, extra_links: dict[str, Iterable[str]] = None
) -> str:
    """Get markdown data for a directory."""

    with IndentedFileWriter.string() as writer:
        writer.write(f"# Directory {LOGO_MARKDOWN} Viewer")
        with writer.padding():
            writer.write("---")

        if extra_links:
            for category, apps in extra_links.items():
                writer.write(f"## {category}")
                with writer.padding():
                    for app in apps:
                        writer.write(f"* [{app}]({app})")

        writer.write(f"## `{path}`")
        writer.empty()

        writer.write("* [..](..)")

        for item in path.iterdir():
            curr = rel(item, base=path)

            name = f"`{curr}`"
            if item.is_dir():
                name = f"**{name}**"

            writer.write(f"* [{name}]({curr})")

        result: str = cast(StringIO, writer.stream).getvalue()

    return result
