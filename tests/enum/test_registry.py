"""
Test the 'enum.registry' module.
"""

# third-party
from pytest import raises

# module under test
from runtimepy.enum.registry import EnumRegistry

# internal
from tests.resources import resource


def test_enum_registry_basic():
    """Test basic interactions with an enum registry."""

    enums = EnumRegistry.decode(resource("enums", "sample_enum.yaml"))
    assert enums.get("int1") is not None
    assert enums.get(1) is not None
    assert enums["bool1"].is_boolean
    assert enums[2].is_boolean
    assert enums[1].is_integer

    with raises(KeyError):
        assert enums["bool2"]

    assert enums.register_dict(
        "bool2",
        {"type": "bool", "items": {"on": True, "off": False}},
    )
    assert not enums.register_dict(
        "int2", {"id": 1, "type": "int", "items": {}}
    )
    assert not enums.register_dict("!@#$", {})
