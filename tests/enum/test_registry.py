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

    assert enums.register_dict(
        "int2",
        {"type": "int", "items": {"on": 1, "off": 0}},
    )

    assert enums.register_dict("bool3", {"type": "bool", "items": {}})
    assert enums["bool3"].register_bool("open", False)
    assert enums["bool3"].register_bool("closed", True)
    assert not enums["bool3"].register_bool("on", True)

    assert enums["bool3"].as_str(False) == "open"
    assert enums["bool3"].as_bool("closed") is True

    enums["bool3"].type.validate(True)
    with raises(ValueError):
        enums["bool3"].type.validate(1)

    assert enums["int1"].as_str(1) == "a"
    assert enums["int1"].as_int("a") == 1
    assert enums["int1"].register_int("d") is not None
