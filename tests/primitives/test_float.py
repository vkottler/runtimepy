"""
Test the 'primitives.float' module.
"""

# module under test
from runtimepy.primitives.float import Half


def test_primitives_half_basic():
    """Test that the half-precision floating-point primitive works."""

    inst = Half()
    assert inst.size == 2

    assert not bool(inst)

    inst(1.0)
    assert inst == 1.0

    assert bool(inst)

    data = bytes(inst)
    assert len(data) == 2

    inst(0.0)

    inst.update(data)

    assert inst == 1.0
