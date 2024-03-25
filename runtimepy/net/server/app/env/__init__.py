"""
A module implementing a channel-environment tab HTML interface.
"""

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server.app.bootstrap.elements import input_box
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.env.modal import Modal
from runtimepy.net.server.app.env.tab import ChannelEnvironmentTab
from runtimepy.net.server.app.placeholder import under_construction


def channel_environments(app: AppInfo, tabs: TabbedContent) -> None:
    """Populate application elements."""

    # Remove tab-content scrolling.
    tabs.set_scroll(False)

    # Tab name filter.
    input_box(tabs.tabs, label="tab")

    # Connection tabs.
    for name, conn in app.connections.items():
        ChannelEnvironmentTab(
            name, conn.command, app, tabs, icon="ethernet"
        ).entry()

    # Task tabs.
    for name, task in app.tasks.items():
        ChannelEnvironmentTab(
            name, task.command, app, tabs, icon="arrow-repeat"
        ).entry()

    # Toggle channel-table button.
    tabs.add_button("Toggle channel table", ".channel-column", icon="table")

    # Application modals.
    Modal(tabs)
    Modal(tabs, name="diagnostics", icon="activity")

    # Placeholder for using space at the bottom of the tab list.
    under_construction(tabs.tabs)
