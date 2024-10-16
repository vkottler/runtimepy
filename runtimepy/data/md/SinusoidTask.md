# Sinusoid Tasks

## Intent

These tasks compute
[`math.sin`](https://docs.python.org/3/library/math.html#math.sin) and
[`math.cos`](https://docs.python.org/3/library/math.html#math.cos) on every
iteration, which advances one "step" per dispatch where the "step angle"
advanced depends on the `steps` control.

Once the current "step angle" is computed, controls `amplitude` and phase
angles are considered for final `sin` and `cos` channel values.

## Discussion

* Is it worth adding a `tan` channel that computes
[`math.tan`](https://docs.python.org/3/library/math.html#math.tan) and/or other
trigonometric functions?
* Is it worth adding a "number of steps" control, such that one task iteration
could advance multiple waveform steps?
