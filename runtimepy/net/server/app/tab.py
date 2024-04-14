"""
A module implementing an application tab interface.
"""

# built-in
from io import StringIO
from typing import cast

# third-party
from svgen.element import Element
from svgen.element.html import div
from vcorelib.io.file_writer import IndentedFileWriter

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server.app.bootstrap import icon_str
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.files import kind_url, write_found_file


class Tab:
    """A simple application-tab interface class."""

    def __init__(
        self,
        name: str,
        app: AppInfo,
        tabs: TabbedContent,
        source: str = None,
        subdir: str = "tab",
        icon: str = None,
    ) -> None:
        """Initialize this instance."""

        self.name = name

        self.source = source if source else self.name
        self.subdir = subdir

        self.app = app
        self.button, self.content = tabs.create(self.name)

        button_str = ""
        if icon:
            button_str += icon_str(icon) + " "
        button_str += self.name
        self.button.text = button_str

        self.init()

        self.compose(self.content)

    def init(self) -> None:
        """Initialize this instance."""

    def compose(self, parent: Element) -> None:
        """Compose the tab's HTML elements."""

    def write_js(self, writer: IndentedFileWriter, **kwargs) -> bool:
        """Write JavaScript code for the tab."""

        return write_found_file(
            writer, kind_url("js", self.source, subdir=self.subdir, **kwargs)
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
