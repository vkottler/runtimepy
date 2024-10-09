"""
A module implementing SSL-related interfaces.
"""

# built-in
import ssl
from typing import Any


def handle_possible_ssl(client: bool = True, **kwargs) -> dict[str, Any]:
    """Handle creating an SSL context based on keyword arguments."""

    args = ["cafile", "capath", "cadata"]
    if (
        kwargs.pop("use_ssl", False)
        or any(x in kwargs for x in args)
        or "certfile" in kwargs
    ):
        context = ssl.create_default_context(
            purpose=(
                ssl.Purpose.SERVER_AUTH if client else ssl.Purpose.CLIENT_AUTH
            ),
            **{x: kwargs.pop(x, None) for x in args},
        )

        if "certfile" in kwargs:
            context.load_cert_chain(
                kwargs.pop("certfile"), keyfile=kwargs.pop("keyfile", None)
            )

        kwargs["ssl"] = context

    return kwargs
