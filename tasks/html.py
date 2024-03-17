"""
A module for working on HTML ideas.
"""

# third-party
from svgen.element import Element
from vcorelib.io.file_writer import IndentedFileWriter

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.files import (
    append_kind,
    kind_url,
    write_found_file,
)
from runtimepy.net.server.app.tab import Tab


class DevTab(Tab):
    """A developmental tab."""

    def populate_elements(self, parent: Element) -> None:
        """Populate tab elements."""

        append_kind(parent, self.name, kind="html", tag="div")

    def init_script(self, writer: IndentedFileWriter) -> None:
        """Initialize script code."""

        write_found_file(writer, kind_url("js", self.name))

    def populate_shown_inner(self, writer: IndentedFileWriter) -> None:
        """Populate the tab-shown handler."""

    def populate_hidden_inner(self, writer: IndentedFileWriter) -> None:
        """Populate the tab-hidden handler."""


def sample(app: AppInfo, tabs: TabbedContent) -> None:
    """Populate application elements."""

    # Add dev tab.
    DevTab("dev", app, tabs).entry()

    for idx in range(100):
        tab = Tab(f"test{idx}", app, tabs)
        tab.entry()
