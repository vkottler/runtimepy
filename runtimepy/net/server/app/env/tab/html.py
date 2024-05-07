"""
A module implementing a channel-environment tab HTML interface.
"""

# built-in
from typing import Optional, cast

# third-party
from svgen.element import Element
from svgen.element.html import div

# internal
from runtimepy.channel import AnyChannel
from runtimepy.enum import RuntimeEnum
from runtimepy.net.server.app.bootstrap.elements import (
    TEXT,
    flex,
    input_box,
    set_tooltip,
    toggle_button,
)
from runtimepy.net.server.app.env.tab.base import ChannelEnvironmentTabBase
from runtimepy.net.server.app.env.widgets import (
    channel_table_header,
    enum_dropdown,
    plot_checkbox,
    value_input_box,
)
from runtimepy.net.server.app.placeholder import under_construction


class ChannelEnvironmentTabHtml(ChannelEnvironmentTabBase):
    """A channel-environment tab interface."""

    def add_channel(
        self,
        parent: Element,
        name: str,
        chan: AnyChannel,
        enum: Optional[RuntimeEnum],
        description: str = None,
    ) -> int:
        """Add a channel to the table."""

        env = self.command.env

        name_elem = div(tag="td", text=name, parent=parent)
        if chan.commandable:
            name_elem.add_class("text-success")

        if description:
            set_tooltip(name_elem, description, placement="left")

        div(
            tag="td",
            class_str="channel-value",
            parent=parent,
            title=f"Current value of '{name}'.",
        )

        # Add boolean/bit toggle button.
        control = div(tag="td", parent=parent)

        kind_str = str(chan.type)

        # Should handle enums at some point.
        if enum is not None:
            enum_name = env.enums.names.name(enum.id)
            assert enum_name is not None
            kind_str = enum_name

        chan_type = div(
            tag="td",
            text=kind_str,
            parent=parent,
            title=f"Underlying primitive type for '{name}'.",
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
                toggle_button(control, id=name, title=f"Toggle '{name}'.")
                control_added = True

        elif chan.type.is_float:
            chan_type.add_class("text-secondary-emphasis")
        else:
            chan_type.add_class("text-primary")

        # Input box with send button.
        if not control_added and chan.commandable:
            value_input_box(name, control)

        return chan.id

    def add_field(
        self, parent: Element, name: str, description: str = None
    ) -> None:
        """Add a bit-field row entry."""

        env = self.command.env

        enum = None
        field = env.fields[name]
        if field.is_enum:
            enum = env.enums[field.enum]

        # Add boolean/bit toggle button.
        is_bit = field.width == 1
        kind_str = f"{'bit' if is_bit else 'bits'} {field.where_str()}"

        name_elem = div(tag="td", text=name, parent=parent)
        if field.commandable:
            name_elem.add_class("text-success")

        if field.description:
            description = field.description
        if description:
            set_tooltip(name_elem, description, placement="left")

        div(
            tag="td",
            class_str="channel-value",
            parent=parent,
            title=f"Current value of '{name}'.",
        )

        control = div(tag="td", parent=parent)
        if field.commandable:
            if is_bit:
                toggle_button(control, id=name, title=f"Toggle '{name}'.")
            elif enum:
                enum_dropdown(control, name, enum, field())
            else:
                value_input_box(name, control)

        div(
            tag="td",
            text=kind_str,
            parent=parent,
            title=f"Field position for '{name}' within underlying primitive.",
        )["class"] = "text-info-emphasis"

    def channel_table(self, parent: Element) -> None:
        """Create the channel table."""

        table = div(tag="table", parent=parent)
        table.add_class("table", TEXT)

        header = div(tag="thead", parent=table)
        body = div(tag="tbody", parent=table)

        # Add header.
        channel_table_header(header)

        env = self.command.env

        # make a table for channel stuff
        for name in env.names:
            row = div(
                tag="tr",
                parent=body,
                id=name,
                class_str="channel-row border-start border-end",
            )

            plot_checkbox(row, name)

            no_desc = f"No description for '{name}'."

            # Add channel rows.
            chan_result = env.get(name)
            if chan_result is not None:
                chan, enum = chan_result
                self.add_channel(
                    row,
                    name,
                    chan,
                    enum,
                    description=(
                        chan.description if chan.description else no_desc
                    ),
                )

            # Add field and flag rows.
            else:
                self.add_field(row, name, description=no_desc)

    def get_id(self, data: str) -> str:
        """Get an HTML id for an element."""
        return f"{self.name}-{data}"

    def compose(self, parent: Element) -> None:
        """Compose the tab's HTML elements."""

        # For controlling layout.
        container = flex(parent=parent)

        # Use all of the vertical space by default.
        parent.add_class("h-100")
        container.add_class("h-100")

        vert_container = flex(
            parent=container,
            kind="column",
        )
        vert_container.add_class("channel-column", "collapse", "show")

        input_box(
            vert_container,
            label="command",
            pattern="help",
            description="Send a string command via this environment.",
            id=self.get_id("command"),
        )

        # Text area.
        logs = div(
            tag="textarea",
            parent=div(parent=vert_container, class_str="form-floating"),
            class_str=f"form-control rounded-0 {TEXT} text-logs",
            id=self.get_id("logs"),
            title=f"Text logs for {self.name}.",
        )
        logs.booleans.add("readonly")

        self.channel_table(vert_container)

        # Possible empty space that could eventually be used (scenario: channel
        # table doesn't take up full vertical space, few channels).
        under_construction(
            vert_container,
            class_str="border-start border-bottom border-end",
            note="unused space",
        )

        # Divider.
        div(
            id=self.get_id("divider"),
            parent=container,
            class_str="vertical-divider border-start",
        )

        # Plot.
        div(
            tag="canvas",
            id=self.get_id("plot"),
            parent=div(parent=container, class_str="w-100 h-100 border-start"),
            class_str="w-100 h-100 click-plot",
        )
