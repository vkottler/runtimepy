class OverlayManager {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = this.canvas.getContext("2d");
    this.bufferDepth = 512;
    this.visible = false;
  }

  update(time) {
    let canvas = this.canvas;
    let ctx = this.ctx;

    /* Clear before drawing. */
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (this.visible) {
      ctx.fillStyle = "#495057";
      let size = 12;

      ctx.fillRect(size, size, size, size);
      ctx.fillRect(canvas.width - (2 * size), size, size, size);
      ctx.fillRect(size, canvas.height - (2 * size), size, size);
      ctx.fillRect(canvas.width - (2 * size), canvas.height - (2 * size), size,
                   size);

      ctx.fillStyle = "#cce2e6";
      let fontSize = 12;
      ctx.font = fontSize + "px monospace";
      let y = fontSize;
      let x = (canvas.width / 3);

      ctx.fillText("bufferDepth=" + this.bufferDepth, x, y);
      y += fontSize;

      ctx.fillText(time, x, y);
    }
  }

  updateSize(width, height) {
    this.canvas.width = width;
    this.canvas.height = height;
  }

  handleMessage(data) {
    if ("type" in data && data["type"] == "click") {
      this.visible = !this.visible;
    } else {
      console.log("Overlay message not handled:");
      console.log(data);
    }
  }

  bumpCapacity(bumpUp) {
    /*
     * need persistent settings for scroll behavior? (configurable?)
     */
    let scale_factor = 1.05;
    let newCapacity = Math.max(16, bumpUp ? this.bufferDepth * scale_factor
                                          : this.bufferDepth / scale_factor);
    this.bufferDepth = Math.round(newCapacity);
    return this.bufferDepth;
  }
}
