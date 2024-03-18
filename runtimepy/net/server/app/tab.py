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

    def __init__(
        self, name: str, app: AppInfo, tabs: TabbedContent, source: str = None
    ) -> None:
        """Initialize this instance."""

        self.name = name
        self.source = source if source else self.name

        self.app = app
        self.button, self.content = tabs.create(self.name)

        # What should we put here?
        self.button.text = self.name

        self.compose(self.content)

    def compose(self, parent: Element) -> None:
        """Compose the tab's HTML elements."""

        append_kind(parent, self.source, kind="html", tag="div")

    def write_js(self, writer: IndentedFileWriter) -> bool:
        """Write JavaScript code for the tab."""

        return write_found_file(
            writer, kind_url("js", self.source, subdir="tabs")
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
                self.write_js(writer)

            writer.write("});")

            div(
                tag="script",
                parent=self.content,
                text=cast(StringIO, writer.stream).getvalue(),
            )
