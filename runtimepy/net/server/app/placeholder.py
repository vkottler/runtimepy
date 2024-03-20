"""
A module implementing some placeholder widget utilities.
"""

# third-party
from svgen.element import Element

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server.app.bootstrap import icon_str
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.elements import div
from runtimepy.net.server.app.tab import Tab


class DummyTab(Tab):
    """A dummy tab for testing."""

    def compose(self, parent: Element) -> None:
        """Compose the tab's HTML elements."""

        for idx in range(10):
            div(parent=parent, text="Hello, world! " + str(idx))


def under_construction(parent: Element) -> Element:
    """Add some 'under construction' content to the tab area."""

    container = div(parent=parent)
    container["class"] = (
        "flex-grow-1 d-flex flex-column justify-content-between"
    )

    # Add content below tabs.
    div(parent=container)

    sample = div(
        text=icon_str("hammer")
        + " UNDER "
        + icon_str("gear-wide-connected")
        + " CONSTRUCTION "
        + icon_str("wrench-adjustable"),
        parent=container,
    )
    sample["class"] = "text-info text-center font-monospace"

    div(parent=container)

    return container


def dummy_tabs(count: int, app: AppInfo, tabs: TabbedContent) -> None:
    """Add some placeholder tabs."""

    for idx in range(count):
        DummyTab(f"test{idx}", app, tabs).entry()
