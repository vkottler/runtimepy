/* Keys from a scroll event to forward to worker thread. */
const modifierKeys = [ "ctrlKey", "shiftKey", "altKey", "metaKey", "type" ];
const scrollEventKeys =
    modifierKeys.concat([ "deltaX", "deltaY", "deltaZ", "deltaMode" ]);
const pointerEventKeys = modifierKeys.concat([
  "altitudeAngle",
  "azimuthAngle",
  "pointerId",
  "width",
  "height",
  "pressure",
  "tangentialPressure",
  "tiltX",
  "tiltY",
  "twist",
  "pointerType",
  "isPrimary",
]);
const keyboardEventKeys =
    modifierKeys.concat([ "code", "key", "location", "repeat" ]);
