"""
A module implementing a channel-environment tab HTML interface.
"""

# third-party
from svgen.element.html import div

# internal
from runtimepy import PKG_NAME
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server.app.bootstrap.elements import input_box
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.env.modal import Modal
from runtimepy.net.server.app.env.tab import ChannelEnvironmentTab
from runtimepy.net.server.app.placeholder import dummy_tabs, under_construction
from runtimepy.net.server.app.sound import SoundTab


def channel_environments(app: AppInfo, tabs: TabbedContent) -> None:
    """Populate application elements."""

    # Remove tab-content scrolling.
    tabs.set_scroll(False)

    # Tab name filter.
    input_box(tabs.tabs, label="tab", description="Tab name filter.")

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

    # Struct tabs.
    for struct in app.structs.values():
        ChannelEnvironmentTab(
            struct.name, struct.command, app, tabs, icon="bucket"
        ).entry()

    # Subprocess tabs.
    for peer in app.peers.values():
        # Host side.
        ChannelEnvironmentTab(
            peer.struct.name, peer.struct.command, app, tabs, icon="cpu-fill"
        ).entry()

        # Remote side.
        assert peer.peer is not None
        ChannelEnvironmentTab(
            peer.peer_name, peer.peer, app, tabs, icon="cpu"
        ).entry()

    # If we are a peer program, load environments.
    # pylint:disable=import-outside-toplevel
    from runtimepy.subprocess.program import PROGRAM

    if PROGRAM is not None:
        # Host side.
        ChannelEnvironmentTab(
            PROGRAM.struct.name,
            PROGRAM.struct.command,
            app,
            tabs,
            icon="cpu-fill",
        ).entry()

        # Remote side.
        assert PROGRAM.peer is not None
        ChannelEnvironmentTab(
            PROGRAM.peer_name, PROGRAM.peer, app, tabs, icon="cpu"
        ).entry()

    # Toggle channel-table button.
    tabs.add_button(
        "Toggle channel table",
        ".channel-column",
        icon="table",
        id="channels-button",
    )

    # Plot settings modal.
    plot_settings = Modal(tabs, name="plot", icon="graph-up")
    under_construction(plot_settings.footer)

    # Experimental features.
    if app.config_param("experimental", False):
        # Sound tab.
        SoundTab("sound", app, tabs, source="sound", icon="boombox").entry()

        dummy_tabs(3, app, tabs)

        # Application modals.
        Modal(tabs)
        Modal(tabs, name="diagnostics", icon="activity")

    # Placeholder for using space at the bottom of the tab list.
    under_construction(
        tabs.tabs, note="unused space", class_str="border-start border-end"
    )

    # Add splash screen element.
    div(id=f"{PKG_NAME}-splash", parent=tabs.container)
