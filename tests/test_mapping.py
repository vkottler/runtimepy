"""
Test the 'mapping' module.
"""

# module under test
from runtimepy.mapping import TwoWayNameMapping


class SampleMapping(TwoWayNameMapping[int]):
    """A sample mapping class for unit-testing purposes."""


class SampleBoolMapping(TwoWayNameMapping[bool]):
    """A sample mapping class for unit-testing purposes."""


def test_mapping_basic():
    """Test basic interactions with the two-way name mapping class."""

    mapping = SampleMapping()
    assert mapping

    mapping = SampleMapping(mapping={1: "a", 2: "b", 3: "c"}, reverse={})
    assert mapping

    mapping = SampleMapping(
        mapping={1: "a", 2: "b", 3: "c"}, reverse={"a": 1, "b": 2, "c": 3}
    )
    assert mapping

    assert mapping.identifier("a") == 1
    assert mapping.identifier(1) == 1
    assert mapping.identifier(4) is None

    assert SampleMapping.int_from_dict({1: "a", 2: "b", 3: "c"})

    assert SampleBoolMapping.bool_from_dict({True: "on", False: "off"})
