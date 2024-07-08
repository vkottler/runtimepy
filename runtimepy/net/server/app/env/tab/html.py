"""
A module implementing a channel-environment tab HTML interface.
"""

# built-in
from typing import Optional

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
from runtimepy.net.server.app.env.tab.controls import (
    ChannelEnvironmentTabControls,
)
from runtimepy.net.server.app.env.widgets import (
    channel_table_header,
    plot_checkbox,
)
from runtimepy.net.server.app.placeholder import under_construction


def channel_color_button(parent: Element, name: str) -> Element:
    """Create a button for changing a channel's plot color."""

    button = toggle_button(
        parent,
        id=f"{name}-line-color",
        icon="activity",
        icon_classes=["fs-5"],
        tooltip=f"Change line color for '{name}'.",
    )
    button.add_class("d-none", "p-1")

    return button


def create_name_td(parent: Element) -> Element:
    """Create a table data entry for channel names."""

    return div(tag="td", parent=parent, class_str="p-0 text-nowrap")


class ChannelEnvironmentTabHtml(ChannelEnvironmentTabControls):
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

        name_td = create_name_td(parent)

        name_elem = div(tag="span", text=name, parent=name_td)
        if chan.commandable:
            name_elem.add_class("text-success")

        if description:
            set_tooltip(name_elem, description, placement="left")

        channel_color_button(name_td, name)

        div(
            tag="td",
            class_str="channel-value p-0",
            parent=parent,
            title=f"Current value of '{name}'.",
        )

        self._handle_controls(parent, name, chan, enum)

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

        name_td = create_name_td(parent)

        name_elem = div(tag="span", text=name, parent=name_td)
        if field.commandable:
            name_elem.add_class("text-success")

        if field.description:
            description = field.description
        if description:
            set_tooltip(name_elem, description, placement="left")

        channel_color_button(name_td, name)

        div(
            tag="td",
            class_str="channel-value p-0",
            parent=parent,
            title=f"Current value of '{name}'.",
        )

        self._bit_field_controls(parent, name, is_bit, enum)

        div(
            tag="td",
            text=kind_str,
            parent=parent,
            title=f"Field position for '{name}' within underlying primitive.",
            class_str="text-info-emphasis text-nowrap p-0 ps-1 pe-1",
        )

    def channel_table(self, parent: Element) -> None:
        """Create the channel table."""

        table = div(tag="table", parent=parent)
        table.add_class("table", TEXT)

        header = div(tag="thead", parent=table)
        body = div(tag="tbody", parent=table)

        # Add header.
        channel_table_header(header, self.command)

        # Table for channels.
        env = self.command.env
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

    def _compose_plot(self, parent: Element) -> None:
        """Compose plot elements."""

        plot_container = div(
            parent=parent,
            class_str="w-100 h-100 border-start position-relative",
        )

        # Plot.
        div(
            tag="canvas",
            id=self.get_id("plot"),
            parent=plot_container,
            class_str="w-100 h-100",
        )

        # Overlay for plot.
        overlay = div(
            class_str="position-absolute top-0 left-0 w-100 h-100",
            parent=plot_container,
        )
        div(
            tag="canvas",
            id=self.get_id("overlay"),
            parent=overlay,
            tabindex=1,
            class_str="w-100 click-plot",
        )

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
            class_str="border-start border-end",
            note="unused space",
        )

        # Divider.
        div(
            id=self.get_id("divider"),
            parent=container,
            class_str="vertical-divider border-start",
        )

        self._compose_plot(container)
