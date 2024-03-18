"""
A module for working on HTML ideas.
"""

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.tab import Tab


def sample(app: AppInfo, tabs: TabbedContent) -> None:
    """Populate application elements."""

    # Add dev tab.
    Tab("dev", app, tabs).entry()

    for idx in range(10):
        Tab(f"test{idx}", app, tabs).entry()
