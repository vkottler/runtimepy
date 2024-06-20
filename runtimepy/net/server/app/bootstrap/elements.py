"""
A module for creating various bootstrap-related elements.
"""

# built-in
from typing import Optional

# third-party
from svgen.element import Element
from svgen.element.html import div

# internal
from runtimepy.net.server.app.bootstrap import icon_str

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
    title: Optional[str] = "toggle value",
    icon_classes: list[str] = None,
    tooltip: str = None,
    **kwargs,
) -> Element:
    """Add a boolean-toggle button."""

    if title and not tooltip:
        kwargs["title"] = title

    button = div(
        tag="button",
        type="button",
        text=icon_str(icon, classes=icon_classes),
        parent=parent,
        class_str="btn " + BOOTSTRAP_BUTTON,
        **kwargs,
    )
    if tooltip:
        set_tooltip(button, tooltip)

    return button


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


def slider(
    min_val: int | float, max_val: int | float, steps: int, **kwargs
) -> Element:
    """Create a phase-control slider element."""

    elem = div(
        tag="input",
        type="range",
        class_str="m-auto form-range slider",
        **kwargs,
    )

    assert min_val < max_val, (min_val, max_val)

    elem["min"] = min_val
    elem["max"] = max_val

    step = (max_val - min_val) / steps
    if isinstance(min_val, int) and isinstance(max_val, int):
        step = int(step)

    elem["step"] = step

    # add tick marks - didn't seem to work (browser didn't render anything)

    # list_name = f"{name}-datalist"
    # elem["list"] = list_name
    # markers = div(tag="datalist", id=list_name, parent=container, front=True)
    # start = float(elem["min"])
    # num_steps = 8
    # step = (float(elem["max"]) - float(elem["min"])) / num_steps
    # for idx in range(num_steps):
    #     div(tag="option", value=start + (idx * step), parent=markers)

    return elem
