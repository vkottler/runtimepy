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
from runtimepy import PKG_NAME
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.elements import div


class Tab:
    """A simple application-tab interface class."""

    def __init__(self, name: str, app: AppInfo, tabs: TabbedContent) -> None:
        """Initialize this instance."""

        self.name = name
        self.app = app
        self.button, self.content = tabs.create(self.name)

        # What should we put here?
        self.button.text = self.name

        self.populate_elements(self.content)

    def populate_elements(self, parent: Element) -> None:
        """Populate tab elements."""

        for idx in range(100):
            div(
                parent=parent,
                text=f"Hello, world! ({idx})" * 10,
                style="white-space: nowrap;",
            )

    def populate_shown_inner(self, writer: IndentedFileWriter) -> None:
        """Populate the tab-shown handler."""

        # where should we source this from?
        writer.write(f"console.log('SHOWN HANDLER FOR {self.name}');")

    def populate_shown(self, writer: IndentedFileWriter) -> None:
        """Populate the tab-shown handler."""

        shown_handler = f"{self.name}_shown_handler"
        writer.write(f"async function {shown_handler}() " + "{")
        with writer.indented():
            self.populate_shown_inner(writer)
        writer.write("}")

        # If this tab is already/currently shown, run the handler now.
        writer.write("let tab = bootstrap.Tab.getInstance(elem);")
        writer.write("if (tab) {")
        with writer.indented():
            writer.write(f"await {shown_handler}();")
        writer.write("}")

        # Add event listener.
        writer.write("elem.addEventListener('shown.bs.tab', async event => {")
        with writer.indented():
            writer.write(f"await {shown_handler}();")
        writer.write("});")

    def populate_hidden_inner(self, writer: IndentedFileWriter) -> None:
        """Populate the tab-hidden handler."""

        # where should we source this from?
        writer.write(f"console.log('HIDDEN HANDLER FOR {self.name}');")

    def populate_hidden(self, writer: IndentedFileWriter) -> None:
        """Populate the tab-hidden handler."""

        hidden_handler = f"{self.name}_hidden_handler"
        writer.write(f"async function {hidden_handler}() " + "{")
        with writer.indented():
            self.populate_hidden_inner(writer)
        writer.write("}")

        # Add event listener.
        writer.write("elem.addEventListener('hidden.bs.tab', async event => {")
        with writer.indented():
            writer.write(f"await {hidden_handler}();")
        writer.write("});")

    @property
    def element_id(self) -> str:
        """Get this tab's element identifier."""
        return f"{PKG_NAME}-{self.name}-tab"

    def init_script(self, writer: IndentedFileWriter) -> None:
        """Initialize script code."""

    def _init_script(self, writer: IndentedFileWriter) -> None:
        """Create this tab's initialization script."""

        writer.write(
            f'let elem = document.getElementById("{self.element_id}");'
        )
        self.init_script(writer)
        self.populate_shown(writer)
        self.populate_hidden(writer)

    def entry(self) -> None:
        """Tab overall script entry."""

        with IndentedFileWriter.string(per_indent=2) as writer:
            # Write initialization-method wrapper.
            writer.write("inits.push(async () => {")

            with writer.indented():
                self._init_script(writer)

            writer.write("});")

            div(
                tag="script",
                parent=self.content,
                text=cast(StringIO, writer.stream).getvalue(),
            )
