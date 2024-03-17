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

    def populate_shown(self, writer: IndentedFileWriter) -> None:
        """Populate the tab-shown handler."""

        # where should we source this from?
        writer.write(f"console.log('SHOWN HANDLER FOR {self.name}');")

    def populate_hidden(self, writer: IndentedFileWriter) -> None:
        """Populate the tab-hidden handler."""

        # where should we source this from?
        writer.write(f"console.log('HIDDEN HANDLER FOR {self.name}');")

    @property
    def element_id(self) -> str:
        """Get this tab's element identifier."""
        return f"{PKG_NAME}-{self.name}-tab"

    def populate_app(self, writer: IndentedFileWriter) -> None:
        """Write a tab's application wrapper."""

        # Tab shown handler.
        shown_handler = f"{self.name}_shown_handler"
        writer.write(f"async function {shown_handler}() " + "{")
        with writer.indented():
            self.populate_shown(writer)
        writer.write("}")

        writer.write(
            f'let elem = document.getElementById("{self.element_id}");'
        )

        # If this tab is already/currently shown, run the handler now.
        writer.write("let tab = bootstrap.Tab.getInstance(elem);")
        writer.write("if (tab) {")
        with writer.indented():
            writer.write(f"await {shown_handler}();")
        writer.write("}")

        # Tab hidden handler.
        hidden_handler = f"{self.name}_hidden_handler"
        writer.write(f"async function {hidden_handler}() " + "{")
        with writer.indented():
            self.populate_hidden(writer)
        writer.write("}")

        # Register handlers.
        writer.write("elem.addEventListener('shown.bs.tab', async event => {")
        with writer.indented():
            writer.write(f"await {shown_handler}();")
        writer.write("});")
        writer.write("elem.addEventListener('hidden.bs.tab', async event => {")
        with writer.indented():
            writer.write(f"await {hidden_handler}();")
        writer.write("});")

    def entry(self) -> None:
        """Tab overall script entry."""

        with IndentedFileWriter.string(per_indent=2) as writer:
            # Write initialization-method wrapper.
            writer.write("inits.push(async () => {")

            with writer.indented():
                self.populate_app(writer)

            writer.write("});")

            div(
                tag="script",
                parent=self.content,
                text=cast(StringIO, writer.stream).getvalue(),
            )
