"""
Test the 'control.step' module.
"""

# module under test
from runtimepy.control.step import ToggleStepper, ToggleStepperTask
from runtimepy.net.arbiter.info import AppInfo


async def controls_test(app: AppInfo) -> int:
    """Test JSON clients in parallel."""

    toggler = list(app.search_tasks(ToggleStepperTask))[0]
    toggler.paused.value = False

    stepper = list(app.search_structs(ToggleStepper))[0]

    stepper.step.toggle()
    stepper.step.toggle()

    stepper.simulate_time.toggle()

    stepper.step.toggle()
    stepper.step.toggle()

    stepper.simulate_time.toggle()

    stepper.step.toggle()
    stepper.step.toggle()

    assert await toggler.dispatch()

    return 0
