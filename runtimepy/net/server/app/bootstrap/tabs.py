"""
A module implementing interfaces for creating tabbed content with bootstrap.
"""

# third-party
from svgen.element import Element

# internal
from runtimepy import PKG_NAME
from runtimepy.net.server.app.bootstrap import icon_str
from runtimepy.net.server.app.elements import div

BOOTSTRAP_BUTTON = "rounded-0 font-monospace button-bodge"


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

    class_str = "nav-link " + BOOTSTRAP_BUTTON
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


def set_tooltip(element: Element, data: str, placement: str = "right") -> None:
    """Set a tooltip on an element."""

    element["data-bs-title"] = data
    element["data-bs-placement"] = placement

    # Should we use another mechanism for this?
    element["class"] += " has-tooltip"


def collapse_button(tooltip: str = None, **kwargs) -> Element:
    """Create a collapse button."""

    collapse = div(
        tag="button",
        type="button",
        text=icon_str("arrows-collapse-vertical"),
        **kwargs,
    )
    collapse["class"] = "btn btn-secondary " + BOOTSTRAP_BUTTON
    if tooltip:
        set_tooltip(collapse, tooltip)

    collapse["data-bs-toggle"] = "collapse"
    collapse["data-bs-target"] = f"#{PKG_NAME}-tabs"

    return collapse


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

        # Collapse button.
        self.button_column = div(parent=self.container)
        self.button_column["class"] = "d-flex flex-column bg-dark h-100"
        self.collapse = collapse_button(
            parent=self.button_column, tooltip="Collapse tabs."
        )

        # Placeholder.
        collapse_button(parent=self.button_column, tooltip="YUP 2")

        # Create tab container.
        self.tabs = div(id=f"{PKG_NAME}-tabs", parent=self.container)
        tabs_class = "bg-dark nav flex-column nav-pills show"

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
