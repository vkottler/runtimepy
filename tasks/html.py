"""
A module for working on HTML ideas.
"""

# internal
from runtimepy.net.arbiter.info import AppInfo
from runtimepy.net.server.app.bootstrap.tabs import TabbedContent
from runtimepy.net.server.app.elements import div


def sample(app: AppInfo, tabs: TabbedContent) -> None:
    """Populate application elements."""

    for idx in range(10):
        item = f"test{idx}"

        button, content = tabs.create(item)

        # what should we put here?
        button.text = item

        for idx in range(100):
            div(
                parent=content,
                text=f"Hello, world! ({idx})",
                style="white-space: nowrap;",
            )

    del app
