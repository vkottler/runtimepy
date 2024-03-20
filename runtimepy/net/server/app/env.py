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
from runtimepy.net.server.app.bootstrap.elements import TEXT, flex
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.elements import div
from runtimepy.net.server.app.placeholder import under_construction
from runtimepy.net.server.app.tab import Tab


def append_class(curr: str, data: str) -> str:
    """A simple class-appending method."""

    if curr:
        curr += " "
    return curr + data


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

        type_sty = ""

        # Should handle enums at some point.
        if enum is not None:
            enum_name = env.enums.names.name(enum.id)
            assert enum_name is not None
            kind_str = enum_name
            type_sty = append_class(type_sty, "fw-bold")

        if chan.type.is_boolean:
            type_sty = append_class(type_sty, "text-primary-emphasis")
        elif chan.type.is_float:
            type_sty = append_class(type_sty, "text-secondary")
        else:
            type_sty = append_class(type_sty, "text-primary")

        div(tag="td", text=kind_str, parent=parent)["class"] = type_sty

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

        kind = f"{'bit' if field.width == 1 else 'bits'} {field.where_str()}"

        div(tag="td", text=kind, parent=parent)["class"] = "text-info-emphasis"

        name_sty = ""
        if field.commandable:
            name_sty += "text-success"
        div(tag="td", text=name, parent=parent)["class"] = name_sty

        div(tag="td", text=str(env.value(name)), parent=parent)

    def channel_table(self, parent: Element) -> None:
        """Create the channel table."""

        table = div(tag="table", parent=parent)
        table["class"] = "show table " + TEXT

        header = div(tag="thead", parent=table)
        body = div(tag="tbody", parent=table)

        # Add header.
        header_row = div(tag="tr", parent=header)
        for heading in ["type", "name", "value"]:
            div(tag="th", scope="col", parent=header_row, text=heading)

        env = self.command.env

        # make a table for channel stuff
        for name in env.names:
            row = div(tag="tr", parent=body)

            # Implement this at some point.
            # if not self.channel_pattern.matches(name):
            #     continue

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

        # Input box / text log area?
        sub_container = flex(kind="column", parent=container)
        under_construction(sub_container)
        self.channel_table(sub_container)
        under_construction(sub_container)

        # Future plot area?
        under_construction(container)
