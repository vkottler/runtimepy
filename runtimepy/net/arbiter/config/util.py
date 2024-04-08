"""
A module implementing utilites for arbiter configuration data interfaces.
"""

# built-in
from typing import Any as _Any
from typing import TypeVar as _TypeVar

# third-party
from vcorelib.dict.env import list_resolve_env_vars

T = _TypeVar("T")


def list_adder(dest: list[T], data: T, front: bool = True) -> None:
    """Handle adding to either the front or back of a list."""

    if front:
        dest.append(data)
    else:
        dest.insert(0, data)


def fix_kwargs(data: dict[str, _Any]) -> dict[str, _Any]:
    """
    Fix data depending on nuances of what some Python interfaces require.
    """

    # Convert some keys to tuples.
    for key in ["local_addr", "remote_addr"]:
        if key in data:
            data[key] = tuple(data[key])

    return data


def fix_args(data: list[_Any], ports: dict[str, int]) -> list[_Any]:
    """Fix positional arguments."""

    for idx, item in enumerate(data):
        # Allow port variables to be used in host strings.
        if isinstance(item, str):
            data[idx] = ":".join(
                str(x)
                for x in list_resolve_env_vars(
                    item.split(":"),
                    env=ports,  # type: ignore
                )
            )

    return data
