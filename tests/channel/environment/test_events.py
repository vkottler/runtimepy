"""
Test primitive events proxied through channel environments.
"""

# third-party
from pytest import mark

# module under test
from runtimepy.channel.environment.sample import sample_env


@mark.asyncio
async def test_channel_environment_events():
    """Test event-driver interfaces via channel environment."""

    env = sample_env()

    env["sample_state"] = "Off"

    assert await env.wait_for_bool("sample_state", False, 0.0)
    assert await env.wait_for_enum("sample_state", "Off", 0.0)

    env["sample_enum"] = "very_long_member_name_1"

    assert await env.wait_for_enum(
        "sample_enum", "very_long_member_name_1", 0.0
    )
    assert await env.wait_for_numeric("sample_enum", 1, 0.0)
    assert await env.wait_for_numeric_isclose("sample_enum", 1, 0.0)

    # Sampling interface.
    samples = []
    async for sample in env.sample_bool_for("sample_state", 0.0):
        samples.append(sample)
    assert len(samples) == 1

    for chan in ["sample_enum", "sample_state"]:
        _samples = []
        async for _sample in env.sample_enum_for(chan, 0.0):
            _samples.append(_sample)
        assert len(_samples) == 1

    __samples = []
    async for __sample in env.sample_int_for("sample_enum", 0.0):
        __samples.append(__sample)
    assert len(__samples) == 1

    ___samples = []
    async for ___sample in env.sample_float_for("sample_float", 0.0):
        ___samples.append(___sample)
    assert len(___samples) == 1
