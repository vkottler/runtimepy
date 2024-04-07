"""
Channel-environment tab widget interfaces.
"""

# built-in
from typing import cast

# third-party
from svgen.element import Element

# internal
from runtimepy.enum import RuntimeEnum
from runtimepy.net.server.app.bootstrap.elements import (
    input_box,
    set_tooltip,
    toggle_button,
)
from runtimepy.net.server.app.elements import div


def plot_checkbox(parent: Element, name: str) -> None:
    """Add a checkbox for individual channel plot status."""

    container = div(tag="td", parent=parent)

    set_tooltip(
        div(
            tag="input",
            type="checkbox",
            value="",
            id=f"plot-{name}",
            allow_no_end_tag=True,
            parent=container,
            class_str="form-check-input",
        ),
        f"Enable plotting channel '{name}'.",
    )


def enum_dropdown(
    parent: Element, name: str, enum: RuntimeEnum, current: int | bool
) -> None:
    """Implement a drop down for enumeration options."""

    title = f"Enumeration selection for '{name}'."
    select = div(
        tag="select",
        parent=parent,
        class_str="form-select",
        title=title,
        id=name,
    )
    select["aria-label"] = title

    for key, val in cast(dict[str, dict[str, int | bool]], enum.asdict())[
        "items"
    ].items():
        opt = div(tag="option", value=val, text=key, parent=select)
        if current == val:
            opt.booleans.add("selected")


def channel_table_header(parent: Element) -> None:
    """Add header row to channel table."""

    # Add header.
    header_row = div(
        tag="tr", parent=parent, class_str="border-start border-end"
    )
    for heading, desc in [
        ("plot", "Toggle plotting for channels."),
        ("name", "Channel names."),
        ("value", "Channel values."),
        ("ctl", "Type-specific channel controls."),
        ("type", "Channel types."),
    ]:
        set_tooltip(
            div(
                tag="th",
                scope="col",
                parent=header_row,
                text=heading,
                class_str="text-secondary",
            ),
            desc,
            placement="bottom",
        )

    # Add some controls.
    ctl_row = div(tag="tr", parent=parent, class_str="border-start border-end")

    # Button for clearing plotted channels.
    toggle_button(
        div(tag="th", parent=ctl_row),
        title="Clear plotted channels.",
        icon="x-lg",
        id="clear-plotted-channels",
    )

    input_box(
        div(tag="th", parent=ctl_row),
        description="Channel name filter.",
        id="channel-filter",
    )
    for _ in range(3):
        div(tag="th", parent=ctl_row)
