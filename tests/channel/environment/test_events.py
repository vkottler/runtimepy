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
