"""
A module for creating various bootstrap-related elements.
"""

# third-party
from svgen.element import Element

# internal
from runtimepy.net.server.app.bootstrap import icon_str
from runtimepy.net.server.app.elements import div

TEXT = "font-monospace"
BOOTSTRAP_BUTTON = f"rounded-0 {TEXT} button-bodge"


def flex(kind: str = "row", **kwargs) -> Element:
    """Get a flexbox row container."""

    container = div(**kwargs)
    container["class"] = f"d-flex flex-{kind}"
    return container


def set_tooltip(element: Element, data: str, placement: str = "right") -> None:
    """Set a tooltip on an element."""

    element["data-bs-title"] = data
    element["data-bs-placement"] = placement

    # Should we use another mechanism for this?
    element["class"] += " has-tooltip"


BUTTON_COLOR = "secondary"


def bootstrap_button(
    text: str, tooltip: str = None, color: str = BUTTON_COLOR, **kwargs
) -> Element:
    """Create a bootstrap button."""

    button = div(
        tag="button",
        type="button",
        text=text,
        **kwargs,
        class_str=f"btn btn-{color} " + BOOTSTRAP_BUTTON,
    )
    if tooltip:
        set_tooltip(button, tooltip)
    return button


def collapse_button(
    target: str,
    tooltip: str = None,
    icon: str = "arrows-collapse-vertical",
    toggle: str = "collapse",
    **kwargs,
) -> Element:
    """Create a collapse button."""

    collapse = bootstrap_button(icon_str(icon), tooltip=tooltip, **kwargs)
    collapse["data-bs-toggle"] = toggle
    collapse["data-bs-target"] = target

    return collapse


def toggle_button(
    parent: Element,
    icon: str = "toggles",
    title: str = "toggle value",
    **kwargs,
) -> Element:
    """Add a boolean-toggle button."""

    return div(
        tag="button",
        type="button",
        text=icon_str(icon),
        parent=parent,
        title=title,
        class_str="btn " + BOOTSTRAP_BUTTON,
        **kwargs,
    )


def input_box(
    parent: Element,
    label: str = "filter",
    pattern: str = ".*",
    description: str = None,
    **kwargs,
) -> None:
    """Create command input box."""

    container = div(parent=parent, class_str="input-group")

    label_elem = div(tag="span", parent=container, text=label)
    label_elem.add_class("input-group-text", "rounded-0", TEXT)

    if description:
        set_tooltip(label_elem, description)

    box = div(
        tag="input",
        type="text",
        placeholder=pattern,
        parent=container,
        name=label,
        title=label + " input",
        **kwargs,
    )
    box.add_class("form-control", "rounded-0", TEXT)
