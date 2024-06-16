/* An array of initialization methods to run. */
let inits = [];

/* View tabs. */
let tabs = {};
let shown_tab = "UNKNOWN";

/*
 * Create a worker from our 'text/js-worker' element.
 */
const worker = new Worker(window.URL.createObjectURL(new Blob(
    Array.prototype.map.call(
        document.querySelectorAll("script[type='text\/js-worker']"),
        (script) => script.textContent,
        ),
    {type : "module"},
    )));

/*
 * Utility methods.
 */

function setupCursorContext(elem, registerMethod) {
  /* Mouse and touch. */
  let startEvents = [ "mousedown", "touchstart" ];
  let moveEvents = [ "mousemove", "touchmove" ];
  let endEvents = [ "mouseup", "touchend" ];

  for (let i = 0; i < startEvents.length; i++) {
    registerMethod(elem, startEvents[i], moveEvents[i], endEvents[i]);
  }
}

function setupCursorMove(elem, down, move, up, handleMove) {
  elem.addEventListener(down, (event) => {
    elem.classList.add("moving");

    document.addEventListener(move, handleMove);
    document.addEventListener(up, (event) => {
      document.removeEventListener(move, handleMove);
      elem.classList.remove("moving");
    }, {once : true});
  });
}

function randomHexColor() {
  return "#" + (Math.random() * 0xFFFFFF << 0).toString(16).padStart(6, "0");
}
