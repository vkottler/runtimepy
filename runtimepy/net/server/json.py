"""
A module implementing basic JSON-object response handling.
"""

# built-in
from json import JSONEncoder
from typing import Any, Optional, TextIO

# third-party
from vcorelib import DEFAULT_ENCODING
from vcorelib.io import ARBITER, JsonObject

# internal
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader


class Encoder(JSONEncoder):
    """A custom JSON encoder."""

    def default(self, o):
        """A simple override for default encoding behavior."""

        if callable(o):
            o = o()

        return o


def traverse_dict(data: dict[str, Any], *paths: str) -> Any:
    """Attempt to traverse a dictionary by path names."""

    error: dict[str, Any] = {"path": {}}

    # Traverse path.
    curr_path = []
    for part in paths:
        if not part:
            continue

        curr_path.append(part)

        if callable(data):
            data = data()

        # Handle error.
        if not isinstance(data, dict):
            error["path"]["part"] = part
            error["path"]["current"] = ".".join(curr_path)
            error["error"] = f"Can't index '{data}' by string key!"
            data = error
            break

        # Handle 'key not found' error.
        if part not in data:
            error["path"]["part"] = part
            error["path"]["current"] = ".".join(curr_path)
            error["error"] = f"Key not found! {data.keys()}"
            data = error
            break

        data = data[part]

    if callable(data):
        data = data()

    return data


def encode_json(
    stream: TextIO,
    response: ResponseHeader,
    data: dict[str, Any],
    response_type: str = "json",
) -> None:
    """Encode a JSON message response."""

    response["Content-Type"] = (
        f"application/{response_type}; charset={DEFAULT_ENCODING}"
    )
    ARBITER.encode_stream(response_type, stream, data, cls=Encoder)
    stream.write("\n")


def json_handler(
    stream: TextIO,
    request: RequestHeader,
    response: ResponseHeader,
    request_data: Optional[bytes],
    data: JsonObject,
) -> None:
    """Create an HTTP response from some JSON object data."""

    del request_data

    # Traverse path.
    data = traverse_dict(data, *request.target.path.split("/")[2:])

    # Use a convention for indexing data to non-dictionary leaf nodes.
    if not isinstance(data, dict):
        data = {"__raw__": data}

    encode_json(stream, response, data)
