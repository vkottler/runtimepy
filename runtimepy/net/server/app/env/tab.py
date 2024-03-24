"""
A module implementing a channel-environment tab HTML interface.
"""

# built-in
from typing import Optional

# third-party
from svgen.element import Element

# internal
from runtimepy.channel import AnyChannel
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
)
from runtimepy.enum import RuntimeEnum
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server.app.bootstrap import icon_str
from runtimepy.net.server.app.bootstrap.elements import (
    TEXT,
    flex,
    input_box,
    toggle_button,
)
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.elements import div
from runtimepy.net.server.app.placeholder import under_construction
from runtimepy.net.server.app.tab import Tab


class ChannelEnvironmentTab(Tab):
    """A channel-environment tab interface."""

    def __init__(
        self,
        name: str,
        command: ChannelCommandProcessor,
        app: AppInfo,
        tabs: TabbedContent,
        icon: str = "alarm",
    ) -> None:
        """Initialize this instance."""

        self.command = command
        super().__init__(name, app, tabs, source="env")

        # Use an icon as the start of the button.
        self.button.text = icon_str(icon) + " " + self.name

    def add_channel(
        self,
        parent: Element,
        name: str,
        chan: AnyChannel,
        enum: Optional[RuntimeEnum],
    ) -> int:
        """Add a channel to the table."""

        env = self.command.env

        kind_str = str(chan.type)

        # Should handle enums at some point.
        if enum is not None:
            enum_name = env.enums.names.name(enum.id)
            assert enum_name is not None
            kind_str = enum_name

        # Add boolean/bit toggle button.
        toggle = div(tag="td", parent=parent)

        chan_type = div(tag="td", text=kind_str, parent=parent)
        if enum is not None:
            chan_type.add_class("fw-bold")

        if chan.type.is_boolean:
            chan_type.add_class("text-primary-emphasis")
            if chan.commandable:
                toggle_button(toggle)

        elif chan.type.is_float:
            chan_type.add_class("text-secondary-emphasis")
        else:
            chan_type.add_class("text-primary")

        name_sty = ""
        if chan.commandable:
            name_sty += "text-success"
        div(tag="td", text=name, parent=parent)["class"] = name_sty

        div(tag="td", text=str(env.value(name)), parent=parent)

        return chan.id

    def add_field(self, parent: Element, name: str) -> None:
        """Add a bit-field row entry."""

        env = self.command.env

        field = env.fields[name]

        toggle = div(tag="td", parent=parent)

        # Add boolean/bit toggle button.
        is_bit = field.width == 1
        kind_str = f"{'bit' if is_bit else 'bits'} {field.where_str()}"

        div(tag="td", text=kind_str, parent=parent)["class"] = (
            "text-info-emphasis"
        )

        name_elem = div(tag="td", text=name, parent=parent)
        if field.commandable:
            name_elem.add_class("text-success")
            if is_bit:
                toggle_button(toggle)

        div(tag="td", text=str(env.value(name)), parent=parent)

    def channel_table(self, parent: Element) -> None:
        """Create the channel table."""

        table = div(tag="table", parent=parent)
        # table.add_class("show")
        table.add_class("table")
        table.add_class(TEXT)

        header = div(tag="thead", parent=table)
        body = div(tag="tbody", parent=table)

        # Add header.
        header_row = div(tag="tr", parent=header)
        for heading in ["", "type", "name", "value"]:
            div(
                tag="th",
                scope="col",
                parent=header_row,
                text=heading,
                class_str="text-secondary",
            )

        # Add some controls.
        ctl_row = div(tag="tr", parent=header)
        div(tag="th", parent=ctl_row)
        div(tag="th", parent=ctl_row)
        input_box(div(tag="th", parent=ctl_row))
        div(tag="th", parent=ctl_row)

        env = self.command.env

        # make a table for channel stuff
        for name in env.names:
            row = div(tag="tr", parent=body)

            # Add channel rows.
            chan_result = env.get(name)
            if chan_result is not None:
                chan, enum = chan_result
                self.add_channel(row, name, chan, enum)

            # Add field and flag rows.
            else:
                self.add_field(row, name)

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

        input_box(vert_container, label="command", pattern="help")

        # Text area.
        logs = div(
            tag="textarea",
            parent=div(parent=vert_container, class_str="form-floating"),
            class_str=f"form-control rounded-0 {TEXT}",
            id=f"{self.name}-logs",
            title="logs",
        )
        logs.booleans.add("readonly")

        self.channel_table(vert_container)

        under_construction(vert_container)

        # Future plot area?
        under_construction(container, note="plot?")
