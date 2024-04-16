class Plot {
  constructor(element, _worker) {
    this.worker = _worker;
    this.canvas = element;

    /* Send off-screen canvas to worker. */
    let offscreen = this.canvas.transferControlToOffscreen();
    let msg = this.messageBase();
    msg["canvas"] = offscreen;
    this.plotMessage(msg, [ offscreen ]);

    /* Use resize observer to handle resize events. */
    this.resizeObserver = new ResizeObserver(
        ((entries, observer) => { this.handle_resize(); }).bind(this));

    /* Handle click events. */
    let plotButton = document.getElementById("runtimepy-plot-button");
    if (plotButton) {
      this.canvas.onclick = (event) => { plotButton.click(); };
    }
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
