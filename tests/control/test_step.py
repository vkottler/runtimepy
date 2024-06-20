"""
Test the 'control.step' module.
"""

# module under test
from runtimepy.control.step import ToggleStepper
from runtimepy.net.arbiter.info import AppInfo


async def controls_test(app: AppInfo) -> int:
    """Test JSON clients in parallel."""

    stepper = list(app.search_structs(ToggleStepper))[0]

    stepper.step.toggle()
    stepper.step.toggle()

    stepper.simulate_time.toggle()

    stepper.step.toggle()
    stepper.step.toggle()

    stepper.simulate_time.toggle()

    stepper.step.toggle()
    stepper.step.toggle()

    return 0
