"""
A module implementing interfaces for creating tabbed content with bootstrap.
"""

# third-party
from svgen.element import Element

# internal
from runtimepy.net.server.app.elements import div


def create_nav_button(
    parent: Element, name: str, item: str, active_tab: bool
) -> Element:
    """Create a navigation button."""

    # Add button.
    button = div(
        tag="button", id=f"{name}-{item}-tab", parent=parent, role="tab"
    )
    button["type"] = "button"
    button["data-bs-toggle"] = "pill"
    button["data-bs-target"] = f"#{name}-{item}"
    button["aria-controls"] = f"{name}-{item}"
    button["aria-selected"] = str(active_tab).lower()

    class_str = "nav-link rounded-0 font-monospace"
    if active_tab:
        class_str += " active"

    button["class"] = class_str

    return button


def create_nav_container(
    parent: Element, name: str, item: str, active_tab: bool
) -> Element:
    """Create a navigation container element."""

    content = div(
        id=f"{name}-{item}", role="tabpanel", tabindex="0", parent=parent
    )
    content["aria-labelledby"] = f"{name}-{item}-tab"

    class_str = "tab-pane fade"
    if active_tab:
        class_str += " show active"
    content["class"] = class_str

    return content


class TabbedContent:
    """A tabbed-content container."""

    def __init__(self, name: str, parent: Element) -> None:
        """Initialize this instance."""

        self.name = name

        # Create application container
        self.container = div(parent=parent)
        self.container["id"] = name
        self.container["data-bs-theme"] = "dark"
        self.container["class"] = "d-flex align-items-start"

        # Create tab container.
        self.tabs = div(parent=self.container)
        tabs_class = "bg-dark nav flex-column nav-pills"

        # Created a custom class to fix scroll behavior.
        tabs_class += " flex-column-scroll-bodge"

        self.tabs["class"] = tabs_class

        # Create content container.
        self.content = div(id=f"{name}-tabContent", parent=self.container)
        content_class = "tab-content"

        # Created a custom class to fix scroll behavior.
        content_class += " tab-content-scroll-bodge"

        self.content["class"] = content_class

        self.active_tab = True

    def create(self, name: str) -> tuple[Element, Element]:
        """Only the first tab is active."""

        button = create_nav_button(self.tabs, self.name, name, self.active_tab)

        # Add content.
        content = create_nav_container(
            self.content, self.name, name, self.active_tab
        )

        if self.active_tab:
            self.active_tab = False

        return button, content
