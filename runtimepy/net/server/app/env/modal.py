"""
A module implementing a simple modal interface.
"""

# third-party
from svgen.element.html import div

# internal
from runtimepy import PKG_NAME
from runtimepy.net.server.app.bootstrap.elements import TEXT
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent


class Modal:
    """A class implementing a simple bootstrap-modal interface."""

    def __init__(
        self,
        tabs: TabbedContent,
        name: str = "settings",
        icon: str = "sliders",
    ) -> None:
        """Initialize this instance."""

        modal_id = f"{PKG_NAME}-{name}"
        label_id = modal_id + "-label"

        # Top-level container.
        modal = div(parent=tabs.container, id=modal_id, tabindex="-1")
        modal.add_class("modal", "fade")
        modal["aria-labelledby"] = label_id

        content = div(
            parent=div(
                parent=modal, class_str="modal-dialog text-light " + TEXT
            ),
            class_str="modal-content rounded-0",
        )

        self.header = div(parent=content, class_str="modal-header")
        div(
            text=name, class_str="modal-title", id=label_id, parent=self.header
        )
        button = div(
            tag="button",
            type="button",
            parent=self.header,
            class_str="btn-close",
        )
        button["data-bs-dismiss"] = "modal"
        button["aria-label"] = "close"

        self.body = div(parent=content, class_str="modal-body")
        self.footer = div(parent=content, class_str="modal-footer")

        # Add toggle button.
        tabs.add_button(
            f"Toggle {name}",
            "#" + modal_id,
            icon=icon,
            toggle="modal",
            id=f"{modal_id}-button",
        )
