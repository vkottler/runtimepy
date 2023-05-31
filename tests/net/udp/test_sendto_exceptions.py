"""
Test special cases for the 'net.udp.connection' module.
"""

# built-in
from asyncio import Event, gather, sleep

# third-party
from pytest import mark

# module under test
from runtimepy.net.udp.connection import NullUdpConnection


@mark.asyncio
async def test_udp_connection_sendto_fail():
    """Test 'sendto' failures with a UDP connection."""

    conn1, conn2 = await NullUdpConnection.create_pair()

    iterations = 0
    sleep_time = 0.05

    signal = Event()

    async def send_spam() -> None:
        """Send messages back and forth."""

        nonlocal iterations
        msg = "Hello, world!"

        while not conn1.disabled and not conn2.disabled:
            conn1.send_text(msg)
            conn2.send_text(msg)
            iterations += 1
            await sleep(sleep_time)

        for _ in range(10):
            conn1.send_text(msg)
            conn2.send_text(msg)
            iterations += 1
            await sleep(sleep_time)

        await signal.wait()

        # Send more (should cause problems).
        for _ in range(10):
            conn1.send_text(msg)
            conn2.send_text(msg)

    async def closer() -> None:
        """Close the two connections."""

        while iterations < 5:
            await sleep(sleep_time)
            conn1.disable("nominal")

        while iterations < 10:
            await sleep(sleep_time)
            conn2.disable("nominal")

        signal.set()

    # Run everything.
    await gather(send_spam(), closer(), conn1.process(), conn2.process())
