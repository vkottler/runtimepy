"""
Test the 'primitives.float' module.
"""

# built-in
from io import BytesIO
from math import isclose

# third-party
from pytest import mark

# module under test
from runtimepy.primitives import Double, Half, Int32


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


@mark.asyncio
async def test_primitive_scaling():
    """Test a basic primitive scaling scenario."""

    prim = Double(scaling=[1.0, 2.0])

    prim.scaled = 5.0
    assert isclose(prim.scaled, 5.0)

    assert await prim.wait_for_isclose(5.0, 0.0)

    int_prim = Int32(scaling=[2.0, 3.0])
    int_prim.scaled = -1.0
    assert isclose(int_prim.scaled, -1)

    int_prim = Int32()
    int_prim.scaled = -2.0
    assert isclose(int_prim.scaled, -2)


def test_primitives_encode_decode():
    """Test simple encoding and decoding interactions."""

    assert Double.decode(Double.encode(1.0)) == 1.0

    with BytesIO() as stream:
        Double.write(1.0, stream)
        stream.seek(0)
        assert Double.read(stream) == 1.0
