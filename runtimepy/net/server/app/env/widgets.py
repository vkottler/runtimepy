"""
Channel-environment tab widget interfaces.
"""

# built-in
from typing import cast

# third-party
from svgen.element import Element

# internal
from runtimepy.enum import RuntimeEnum
from runtimepy.net.server.app.bootstrap.elements import input_box, set_tooltip
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
    """Add header row to channel table.."""

    # Add header.
    header_row = div(tag="tr", parent=parent)
    for heading, desc in [
        ("plot", "Toggle plotting for channels."),
        ("ctl", "Type-specific channel controls."),
        ("type", "Channel types."),
        ("name", "Channel names."),
        ("value", "Channel values."),
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
    ctl_row = div(tag="tr", parent=parent)
    for _ in range(3):
        div(tag="th", parent=ctl_row)
    input_box(
        div(tag="th", parent=ctl_row),
        description="Channel name filter.",
        id="channel-filter",
    )
    div(tag="th", parent=ctl_row)
