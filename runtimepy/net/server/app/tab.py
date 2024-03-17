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

        for idx in range(10):
            div(
                parent=parent,
                text=f"Hello, world! ({idx})" * 10,
                style="white-space: nowrap;",
            )

    def populate_shown_inner(self, writer: IndentedFileWriter) -> None:
        """Populate the tab-shown handler."""

        self.send_message(writer, 'kind: "tab.shown"')

    def populate_shown(self, writer: IndentedFileWriter) -> None:
        """Populate the tab-shown handler."""

        shown_handler = f"{self.name}_shown_handler"
        writer.write(f"async function {shown_handler}() " + "{")
        with writer.indented():
            self.populate_shown_inner(writer)
        writer.write("}")

        # If this tab is already/currently shown, run the handler now.
        writer.write("if (bootstrap.Tab.getInstance(elem)) {")
        with writer.indented():
            writer.write(f"await {shown_handler}();")
        writer.write("}")

        # Add event listener.
        writer.write("elem.addEventListener('shown.bs.tab', async event => {")
        with writer.indented():
            writer.write(f"await {shown_handler}();")
        writer.write("});")

    def send_message(self, writer: IndentedFileWriter, data: str) -> None:
        """Send a message to the worker thread."""

        writer.write("send_message({" + data + "});")

    def populate_hidden_inner(self, writer: IndentedFileWriter) -> None:
        """Populate the tab-hidden handler."""

        self.send_message(writer, 'kind: "tab.hidden"')

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

    def init_script(self, writer: IndentedFileWriter) -> None:
        """Initialize script code."""

    def _init_script(self, writer: IndentedFileWriter) -> None:
        """Create this tab's initialization script."""

        writer.c_comment("Useful constants.")

        # Declare useful variables.
        writer.write(f'const name = "{self.name}";')
        writer.write(
            (
                "const elem = document.getElementById("
                f'"{PKG_NAME}-" + name + "-tab");'
            )
        )

        # Declare a function for sending messages.
        with writer.padding():
            writer.c_comment("Worker/server messaging interface.")
            writer.write("function send_message(data) {")
            with writer.indented():
                writer.write(
                    'worker.postMessage({name: "'
                    + self.name
                    + '", event: data});'
                )
            writer.write("}")

        writer.c_comment("Tab-specific code start.")
        self.init_script(writer)
        writer.c_comment("Tab-specific code end.")

        with writer.padding():
            writer.c_comment("Tab-shown handling.")
            self.populate_shown(writer)

        writer.c_comment("Tab-hidden handling.")
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
