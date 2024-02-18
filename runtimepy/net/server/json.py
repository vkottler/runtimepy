"""
A module implementing basic JSON-object response handling.
"""

# built-in
from typing import Any, Optional, TextIO

# third-party
from vcorelib import DEFAULT_ENCODING
from vcorelib.io import ARBITER, JsonObject

# internal
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader


def json_handler(
    stream: TextIO,
    request: RequestHeader,
    response: ResponseHeader,
    request_data: Optional[bytes],
    data: JsonObject,
) -> None:
    """Create an HTTP response from some JSON object data."""

    del request_data

    response_type = "json"
    response["Content-Type"] = (
        f"application/{response_type}; charset={DEFAULT_ENCODING}"
    )

    error: dict[str, Any] = {"path": {}}

    # Traverse path.
    curr_path = []
    for part in request.target.path.split("/")[2:]:
        if not part:
            continue

        curr_path.append(part)

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

        data = data[part]  # type: ignore

    # Use a convention for indexing data to non-dictionary leaf nodes.
    if not isinstance(data, dict):
        data = {"__raw__": data}

    ARBITER.encode_stream(response_type, stream, data)
    stream.write("\n")
