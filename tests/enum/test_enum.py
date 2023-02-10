"""
Test the 'enum' module.
"""

# built-in
from enum import IntEnum, auto

# module under test
from runtimepy.enum import RuntimeEnum


class SampleEnum(IntEnum):
    """A sample enumeration."""

    A = auto()
    B = auto()
    C = auto()


def test_runtime_enum_from_enum():
    """Test that we can create a runtime enumeration from a class."""

    enum = RuntimeEnum.from_enum(SampleEnum, 1)
    assert enum.get_int("a")
    assert enum.get_int("b")
    assert enum.get_int("c")
