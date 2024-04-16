"""
A module implementing a tab for experimenting with sound generation.
"""

# third-party
from svgen.element import Element
from svgen.element.html import div

# built-in
from runtimepy.net.server.app.bootstrap.elements import bootstrap_button
from runtimepy.net.server.app.tab import Tab


class SoundTab(Tab):
    """A simple sound-tab interface class."""

    def compose(self, parent: Element) -> None:
        """Compose the tab's HTML elements."""

        container = div(parent=parent, class_str="text-light")

        div(text="Hello, world! 1", parent=container)
        div(text="Hello, world! 2", parent=container)
        div(text="Hello, world! 3", parent=container)

        # Add a button that we can hook up code to.
        bootstrap_button(
            "TEST", color="primary", parent=container, id="test-button"
        )
