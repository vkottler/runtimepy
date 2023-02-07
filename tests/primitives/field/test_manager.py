"""
Test the 'primitives.field.manager' module.
"""

# built-in
from copy import copy

# module under test
from runtimepy.enum.registry import EnumRegistry
from runtimepy.primitives.field.manager import (
    BitFieldsManager,
    fields_from_file,
)
from runtimepy.registry.name import NameRegistry

# internal
from tests.resources import resource


def test_bit_fields_manager_basic():
    """Test basic interactions with a bit-fields manager."""

    manager = BitFieldsManager(
        NameRegistry(),
        EnumRegistry.decode(
            resource("channels", "environment", "sample", "enums.json")
        ),
        fields_from_file(
            resource("channels", "environment", "sample", "fields.json")
        ),
    )

    copied = copy(manager)

    assert manager.get("field1") == "off"
    assert copied.get("field1") == "off"

    manager.set("field1", "on")

    assert manager.get("field1") == "on"
    assert copied.get("field1") == "off"
