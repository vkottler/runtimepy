class Plot {
  constructor(element, _worker, overlay) {
    this.worker = _worker;
    this.canvas = element;

    this.overlay = overlay;
    let offscreenOverlay = this.overlay.transferControlToOffscreen();

    /* Send off-screen canvas to worker. */
    let offscreen = this.canvas.transferControlToOffscreen();
    let msg = this.messageBase();
    msg["canvas"] = offscreen;
    msg["overlay"] = offscreenOverlay;
    this.plotMessage(msg, [ offscreen, offscreenOverlay ]);

    /* Use resize observer to handle resize events. */
    this.resizeObserver = new ResizeObserver(
        ((entries, observer) => { this.handle_resize(); }).bind(this));

    /* Handle overlay events. */
    if (this.overlay) {
      /* Scroll, click and keyboard. */
      this.overlay.onwheel = this.createEventSender(scrollEventKeys);
      this.overlay.onclick = this.createEventSender(pointerEventKeys);
      let eventHandler = this.createEventSender(keyboardEventKeys);
      this.overlay.addEventListener("keydown", eventHandler);
      this.overlay.addEventListener("keyup", eventHandler);

      /* Should there be a keybind that opens this? */
      // let plotButton = document.getElementById("runtimepy-plot-button");
    }
  }

  createEventSender(keys) {
    let result = (event) => {
      let msg = {};
      for (const key of keys) {
        if (key in event) {
          msg[key] = event[key];
        }
      }
      this.plotMessage({"message" : msg});
    };
    return result.bind(this);
  }

  plotMessage(data, param) { this.worker.toWorker({"plot" : data}, param); }

  messageBase() {
    return {
      "width" : this.canvas.clientWidth,
      "height" : this.canvas.clientHeight
    };
  }

  handle_resize() { this.plotMessage(this.messageBase()); }

  handle_shown(is_shown) {
    if (is_shown) {
      this.resizeObserver.observe(this.canvas);
    } else {
      this.resizeObserver.unobserve(this.canvas);
    }
    this.plotMessage({"shown" : is_shown});
  }
}
