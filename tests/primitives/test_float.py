"""
Test the 'primitives.float' module.
"""

# built-in
from io import BytesIO
from math import isclose

# module under test
from runtimepy.primitives.float import Double, Half


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

    assert inst.age_str()


def test_primitive_scaling():
    """Test a basic primitive scaling scenario."""

    prim = Double(scaling=[1.0, 2.0])

    prim.scaled = 5.0
    assert isclose(prim.scaled, 5.0)


def test_primitives_encode_decode():
    """Test simple encoding and decoding interactions."""

    assert Double.decode(Double.encode(1.0)) == 1.0

    with BytesIO() as stream:
        Double.write(1.0, stream)
        stream.seek(0)
        assert Double.read(stream) == 1.0
