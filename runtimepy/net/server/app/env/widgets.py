"""
Channel-environment tab widget interfaces.
"""

# built-in
from typing import cast

# third-party
from svgen.element import Element
from svgen.element.html import div

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.enum import RuntimeEnum
from runtimepy.net.server.app.bootstrap.elements import (
    flex,
    input_box,
    set_tooltip,
    toggle_button,
)


def plot_checkbox(parent: Element, name: str) -> None:
    """Add a checkbox for individual channel plot status."""

    container = div(tag="td", parent=parent, class_str="text-center")

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
        placement="left",
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


def channel_table_header(parent: Element, env: ChannelEnvironment) -> None:
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
            placement="left",
        )

    # Add some controls.
    ctl_row = div(tag="tr", parent=parent, class_str="border-start border-end")

    # Button for clearing plotted channels.
    toggle_button(
        div(tag="th", parent=ctl_row),
        tooltip="Clear plotted channels.",
        icon="x-lg",
        id="clear-plotted-channels",
    )

    input_box(
        div(tag="th", parent=ctl_row),
        description="Channel name filter.",
        id="channel-filter",
    )

    # Button for clearing plot points.
    toggle_button(
        div(tag="th", parent=ctl_row),
        icon="trash",
        tooltip="Clear all plot points.",
        id="clear-plotted-points",
    )

    # Button for 'reset all defaults' if this tab has more than one channel
    # with a default value.
    if env.num_defaults > 1:
        cell = div(tag="th", parent=ctl_row)
        toggle_button(
            cell,
            id="set-defaults",
            icon="arrow-counterclockwise",
            tooltip="Reset all channels to their default values.",
        )
    else:
        div(tag="th", parent=ctl_row)

    # Empty for now.
    div(tag="th", parent=ctl_row)


def value_input_box(name: str, parent: Element) -> Element:
    """Create an input box for channel values."""

    input_container = flex(parent=parent)
    div(
        tag="input",
        type="text",
        parent=input_container,
        title=f"Set command value for '{name}'.",
        id=name,
    ).add_class(
        "channel-value-input",
        "rounded-0",
        "font-monospace",
        "form-control",
    )
    toggle_button(
        input_container,
        icon="send",
        id=name,
        title=f"Send command value for '{name}'.",
    )

    return input_container
