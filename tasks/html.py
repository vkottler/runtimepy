"""
A module for working on HTML ideas.
"""

# third-party
from svgen.element import Element
from vcorelib.io.file_writer import IndentedFileWriter

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.elements import div
from runtimepy.net.server.app.tab import Tab


class DevTab(Tab):
    """A developmental tab."""

    def populate_elements(self, parent: Element) -> None:
        """Populate tab elements."""

        div(parent=parent, text=f"Dev tab {self.name}.")

    def populate_shown(self, writer: IndentedFileWriter) -> None:
        """Populate the tab-shown handler."""

        writer.write(f"console.log('shown dev tab {self.name}');")

    def populate_hidden(self, writer: IndentedFileWriter) -> None:
        """Populate the tab-hidden handler."""

        writer.write(f"console.log('hidden dev tab {self.name}');")


def sample(app: AppInfo, tabs: TabbedContent) -> None:
    """Populate application elements."""

    # Add dev tab.
    DevTab("dev", app, tabs).entry()

    for idx in range(100):
        tab = Tab(f"test{idx}", app, tabs)
        tab.entry()
