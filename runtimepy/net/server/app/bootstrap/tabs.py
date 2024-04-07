"""
A module implementing interfaces for creating tabbed content with bootstrap.
"""

# third-party
from svgen.element import Element

# internal
from runtimepy import PKG_NAME
from runtimepy.net.server.app.bootstrap.elements import (
    BOOTSTRAP_BUTTON,
    collapse_button,
)
from runtimepy.net.server.app.elements import div


def create_nav_button(
    parent: Element,
    name: str,
    item: str,
    active_tab: bool,
    **kwargs,
) -> Element:
    """Create a navigation button."""

    # Add button.
    button = div(
        tag="button",
        id=f"{name}-{item}-tab",
        parent=parent,
        role="tab",
        title=f"Navigate to '{item}' tab.",
        **kwargs,
    )
    button["type"] = "button"
    button["data-bs-toggle"] = "pill"
    button["data-bs-target"] = f"#{name}-{item}"
    button["aria-controls"] = f"{name}-{item}"
    button["aria-selected"] = str(active_tab).lower()

    button.add_class("nav-link", BOOTSTRAP_BUTTON)
    if active_tab:
        button.add_class("active")

    return button


def create_nav_container(
    parent: Element, name: str, item: str, active_tab: bool
) -> Element:
    """Create a navigation container element."""

    content = div(
        id=f"{name}-{item}", role="tabpanel", tabindex="0", parent=parent
    )
    content["aria-labelledby"] = f"{name}-{item}-tab"

    content.add_class("tab-pane", "fade")
    if active_tab:
        content.add_class("show", "active")

    return content


class TabbedContent:
    """A tabbed-content container."""

    def add_button(self, msg: str, target: str, **kwargs) -> Element:
        """Add a button to the left side button column."""

        return collapse_button(
            target,
            parent=self.button_column,
            tooltip=f"{msg}.",
            title=f"{msg} button.",
            **kwargs,
        )

    def __init__(self, name: str, parent: Element) -> None:
        """Initialize this instance."""

        self.name = name

        # Create application container.
        self.container = div(parent=parent, id=name)
        self.container.add_class("d-flex", "align-items-start")

        # Dark theme.
        self.container["data-bs-theme"] = "dark"
        parent.add_class("bg-dark")

        # Buttons.
        self.button_column = div(parent=self.container)
        self.button_column.add_class(
            "d-flex", "flex-column", "h-100", "bg-secondary-subtle"
        )

        # Toggle tabs button.
        self.add_button("Toggle tabs", f"#{PKG_NAME}-tabs", id="tabs-button")

        # Create tab container.
        self.tabs = div(id=f"{PKG_NAME}-tabs", parent=self.container)
        self.tabs.add_class(
            "nav",
            "flex-column",
            "nav-pills",
            "show",
            "flex-column-scroll-bodge",
        )

        # Create content container.
        self.content = div(id=f"{name}-tabContent", parent=self.container)
        self.set_scroll(True)

        self.active_tab = True

    def set_scroll(self, scroll: bool) -> None:
        """Set classes on content element."""

        self.content["class"] = ""
        self.content.add_class("tab-content", "tab-content-bodge")
        if scroll:
            self.content.add_class("scroll")

    def create(self, name: str) -> tuple[Element, Element]:
        """Only the first tab is active."""

        button = create_nav_button(
            self.tabs,
            self.name,
            name,
            self.active_tab,
            class_str="border-start border-bottom border-end",
        )

        # Add content.
        content = create_nav_container(
            self.content, self.name, name, self.active_tab
        )

        if self.active_tab:
            self.active_tab = False

        return button, content
