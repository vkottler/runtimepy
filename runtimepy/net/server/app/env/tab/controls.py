"""
A module implementing channel control HTML rendering.
"""

# built-in
from typing import Optional, cast

# third-party
from svgen.element import Element
from svgen.element.html import div

# internal
from runtimepy.channel import AnyChannel
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.enum import RuntimeEnum
from runtimepy.net.server.app.bootstrap.elements import slider, toggle_button
from runtimepy.net.server.app.env.tab.base import ChannelEnvironmentTabBase
from runtimepy.net.server.app.env.widgets import (
    TABLE_BUTTON_CLASSES,
    enum_dropdown,
    value_input_box,
)


def get_channel_kind_str(
    env: ChannelEnvironment, chan: AnyChannel, enum: Optional[RuntimeEnum]
) -> str:
    """Get a string for this channel's type for a UI."""

    kind_str = str(chan.type)
    if enum is not None:
        enum_name = env.enums.names.name(enum.id)
        assert enum_name is not None
        kind_str = enum_name

    return kind_str


def default_button(
    parent: Element,
    name: str,
    chan: AnyChannel,
    *classes: str,
    front: bool = True,
) -> Element:
    """Create a default-value button."""

    button = toggle_button(
        parent,
        id=name,
        icon="arrow-counterclockwise",
        title=f"Reset '{name}' to default value '{chan.default}'.",
        value=chan.default,
        front=front,
    )
    button.add_class("default-button", *classes)
    return button


class ChannelEnvironmentTabControls(ChannelEnvironmentTabBase):
    """A channel-environment tab interface."""

    def _handle_controls(
        self,
        parent: Element,
        name: str,
        chan: AnyChannel,
        enum: Optional[RuntimeEnum],
    ) -> None:
        """Handle channel controls."""

        env = self.command.env

        # Add boolean/bit toggle button.
        control = div(tag="td", parent=parent, class_str="p-0")

        chan_type = div(
            tag="td",
            text=get_channel_kind_str(env, chan, enum),
            parent=parent,
            title=f"Underlying primitive type for '{name}'.",
            class_str="p-0 ps-1 pe-1",
        )

        control_added = False

        if enum:
            chan_type.add_class("fw-bold")

            if chan.commandable and not chan.type.is_boolean:
                enum_dropdown(control, name, enum, cast(int, chan.raw.value))
                control_added = True

        if chan.type.is_boolean:
            chan_type.add_class("text-primary-emphasis")
            if chan.commandable:
                button = toggle_button(
                    control, id=name, title=f"Toggle '{name}'."
                )
                button.add_class("toggle-value", *TABLE_BUTTON_CLASSES)
                control_added = True

                if chan.default is not None:
                    default_button(
                        control, name, chan, *TABLE_BUTTON_CLASSES, front=False
                    )

        elif chan.type.is_float:
            chan_type.add_class("text-secondary-emphasis")
        else:
            chan_type.add_class("text-primary")

        # Input box with send button.
        if not control_added and chan.commandable:
            container = value_input_box(name, control)

            # Reset-to-default button if a default value exists.
            if chan.default is not None:
                default_button(container, name, chan, *TABLE_BUTTON_CLASSES)

            if chan.controls:
                # Determine if a slider should be created.
                if "slider" in chan.controls:
                    elem = chan.controls["slider"]

                    slider(
                        elem["min"],  # type: ignore
                        elem["max"],  # type: ignore
                        int(elem["step"]),  # type: ignore
                        parent=container,
                        id=name,
                        title=f"Value control for '{name}'.",
                        front=True,
                    )

    def _bit_field_controls(
        self,
        parent: Element,
        name: str,
        is_bit: bool,
        enum: Optional[RuntimeEnum],
    ) -> None:
        """Add control elements for bit fields."""

        control = div(tag="td", parent=parent, class_str="p-0")

        field = self.command.env.fields[name]
        if field.commandable:
            if is_bit:
                button = toggle_button(
                    control, id=name, title=f"Toggle '{name}'."
                )
                button.add_class("toggle-value", *TABLE_BUTTON_CLASSES)
            elif enum:
                enum_dropdown(control, name, enum, field())
            else:
                value_input_box(name, control)
