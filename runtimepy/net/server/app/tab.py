"""
A module implementing an application tab interface.
"""

# built-in
from io import StringIO
from typing import cast

# third-party
from svgen.element import Element
from vcorelib.io.file_writer import IndentedFileWriter

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.elements import div
from runtimepy.net.server.app.files import (
    append_kind,
    kind_url,
    write_found_file,
)


class Tab:
    """A simple application-tab interface class."""

    def __init__(self, name: str, app: AppInfo, tabs: TabbedContent) -> None:
        """Initialize this instance."""

        self.name = name
        self.app = app
        self.button, self.content = tabs.create(self.name)

        # What should we put here?
        self.button.text = self.name

        self.compose(self.content)

    def compose(self, parent: Element) -> None:
        """Compose the tab's HTML elements."""

        if append_kind(parent, self.name, kind="html", tag="div") is None:
            for idx in range(100):
                div(parent=parent, text=f"Hello, world! ({idx})")

    def write_js(self, writer: IndentedFileWriter) -> bool:
        """Write JavaScript code for the tab."""

        return write_found_file(
            writer, kind_url("js", self.name, subdir="tabs")
        )

    def entry(self) -> None:
        """Tab overall script entry."""

        with IndentedFileWriter.string(per_indent=2) as writer:
            # Write initialization-method wrapper.
            writer.write("inits.push(async () => {")

            with writer.indented():
                writer.write(
                    f'const tab = new TabInterface("{self.name}", worker);'
                )
                writer.empty()
                result = self.write_js(writer)

            writer.write("});")

            if result:
                div(
                    tag="script",
                    parent=self.content,
                    text=cast(StringIO, writer.stream).getvalue(),
                )
