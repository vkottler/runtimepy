"""
A module implementing an application-settings modal.
"""

# third-party
from svgen.element.html import div

# internal
from runtimepy.net.html.bootstrap.elements import flex, slider
from runtimepy.net.html.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.env.modal import Modal
from runtimepy.net.server.app.placeholder import under_construction


def plot_settings(tabs: TabbedContent) -> None:
    """Create the plot settings modal."""

    modal = Modal(tabs, name="plot", icon="graph-up")
    under_construction(modal.footer)

    div(tag="h1", text="settings", parent=modal.body)
    div(tag="hr", parent=modal.body)

    div(tag="h2", text="plot status", parent=modal.body)
    div(id="plot-status-inner", parent=modal.body)
    div(tag="hr", parent=modal.body)

    div(tag="h2", text="minimum transmit period (ms)", parent=modal.body)

    div(
        tag="p",
        text=(
            "Can be used to throttle the rate of "
            "client <-> server communication. Use the 'ui' tab's metrics to "
            "determine performance impact. Note that only this browser tab's "
            "messaging rate can be controlled (not other connected clients')."
        ),
        parent=modal.body,
    )

    container = flex(parent=modal.body)

    div(
        text="0 ms ('high', run at native refresh rate)",
        parent=container,
        class_str="text-nowrap text-body-emphasis",
    )

    slider(
        0, 100, 100, parent=container, value=0, id="setting-min-tx-period-ms"
    ).add_class("ms-3 me-3")

    div(
        text="100 ms ('low', 10 Hz)",
        parent=container,
        class_str="text-nowrap text-body-emphasis",
    )

    div(tag="hr", parent=modal.body)
