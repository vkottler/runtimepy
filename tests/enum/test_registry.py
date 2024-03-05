"""
Test the 'enum.registry' module.
"""

# third-party
from pytest import raises
from vcorelib.paths.context import tempfile

# module under test
from runtimepy.enum.registry import EnumRegistry, RuntimeIntEnum

# internal
from tests.resources import resource


class SampleEnum(RuntimeIntEnum):
    """A sample enumeration."""

    A = 1
    B = 2
    C = 3


def test_runtime_int_enum_basic():
    """Test basic interations with a runtime integer enumeration."""

    assert SampleEnum.normalize(SampleEnum.A) is SampleEnum.A
    assert SampleEnum.normalize("a") is SampleEnum.A
    assert SampleEnum.normalize("A") is SampleEnum.A
    assert SampleEnum.normalize(1) is SampleEnum.A


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

    assert (
        enums.register_dict(
            "bool2",
            {"type": "bool", "items": {"on": True, "off": False}},
        )
        is not None
    )
    assert (
        enums.register_dict("int2", {"id": 1, "type": "int", "items": {}})
        is None
    )
    assert enums.register_dict("!@#$", {}) is None

    assert (
        enums.register_dict(
            "int2",
            {"type": "int", "items": {"on": 1, "off": 2}},
        )
        is not None
    )

    assert (
        enums.register_dict("bool3", {"type": "bool", "items": {}}) is not None
    )
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

    # Test an invalid name.
    assert (
        enums.register_dict("My Boolean", {"type": "bool", "items": {}})
        is None
    )

    # Test registering an enumeration with no items.
    enum = enums.register_dict("bool4", {"type": "bool"})
    assert enum is not None
    assert enum.register_bool("on", True)
    assert enum.register_bool("off", False)

    # Test that we can encode and decode the updated registry.
    with tempfile(suffix=".json") as tmp:
        enums.encode(tmp)
        new_enums = EnumRegistry.decode(tmp)
        assert enums == new_enums

    # Test a name expected to be valid.
    assert enums.register_dict(
        "sharer.actuator-1.control_mode.cmd", {"type": "int", "items": {}}
    )
