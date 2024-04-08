"""
A module implementing interfaces for working with channel scaling polynomials.
"""

# built-in
from typing import Union

Numeric = Union[float, int]
ChannelScaling = list[Numeric]


def invert(
    value: Numeric, scaling: ChannelScaling = None, should_round: bool = False
) -> Numeric:
    """Apply a scaling polynomial to a value."""

    if scaling:
        # We can't invert a scaling polynomial with more than two terms.
        assert len(scaling) <= 2

        value = float(value)

        offset = scaling[0]
        scale = 1.0
        if len(scaling) > 1:
            scale = scaling[1]

        value -= offset
        value /= scale

    if should_round:
        value = round(value)

    return value


def apply(value: Numeric, scaling: ChannelScaling = None) -> Numeric:
    """Apply a scaling polynomial to a value."""

    if scaling:
        value = float(value)

        result = 0.0  # solve via accumulating
        poly_index_val = 1.0  # self.raw ^ 0
        for scalar in scaling:
            result += scalar * poly_index_val
            poly_index_val *= value
    else:
        result = value

    return result
