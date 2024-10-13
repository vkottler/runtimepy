const defaultPadTo = "                        ";

function padStringTo(data, padTo = defaultPadTo, front = true) {
  let delta = padTo.length - data.length;

  /* Should check if the string was too long. */
  if (delta > 0) {
    let padding = padTo.slice(0, delta);
    data = front ? padding + data : data + padding;
  }

  return data;
}

class OverlayManager {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = this.canvas.getContext("2d");

    /* Runtime state. */
    this.visible = true;
    this.bufferDepth = Math.min(512, this.canvas.width);
    this.minTimestamp = null;
    this.maxTimestamp = null;
    this.lines = [];
    this.maxLen = 0;

    /* Make this controllable at some point. */
    this.fontSize = 14;
  }

  writeLn(data) {
    let padded = padStringTo(data);
    this.maxLen = Math.max(this.maxLen, padded.length);
    this.lines.push(padded);
  }

  update(time) {
    let canvas = this.canvas;
    let ctx = this.ctx;

    /* Clear before drawing. */
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    /* Drawing settings. */
    ctx.font = this.fontSize + "px monospace";
    ctx.fillStyle = "#cce2e6";

    /* Always display frame time. */
    this.writeLn(String((time / 1000).toFixed(3)) + " s (frame time )");

    if (this.visible) {
      /* Corner fiducials. */
      // ctx.fillStyle = "#495057";
      // let size = fontSize * 2;
      // ctx.fillRect(size, size, size, size);
      // ctx.fillRect(canvas.width - (2 * size), size, size, size);
      // ctx.fillRect(size, canvas.height - (2 * size), size, size);
      // ctx.fillRect(canvas.width - (2 * size), canvas.height - (2 * size),
      // size, size);

      /* Show amount of time captured. */
      if (this.minTimestamp != null && this.maxTimestamp) {
        let nanos = nanosString(this.maxTimestamp - this.minTimestamp);
        this.writeLn(nanos[0] + nanos[1] + "s (x-axis     )");
      }

      this.writeLn(String(this.bufferDepth) + "       (max samples)");

      /* Height and width. */
      this.writeLn(String(canvas.width) + "       (width      )");
      this.writeLn(String(canvas.height) + "       (height     )");
      this.writeLn("");
      this.writeLn("Click to hide.");
    } else {
      this.writeLn("");
      this.writeLn("Click for overlay.");
    }

    this.writeLines(canvas.width - (this.maxLen * (this.fontSize * 0.6)),
                    this.fontSize / 2);
  }

  writeLines(x, y) {
    /* Draw lines. */
    for (const line of this.lines) {
      y += this.fontSize;
      if (line) {
        this.ctx.fillText(line, x, y);
      }
    }

    /* Reset state. */
    this.lines = [];
    this.maxLen = 0;
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
