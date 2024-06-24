class PlotDrawer {
  constructor(canvas, colors, overlay) {
    this.canvas = canvas;

    this.overlay = new OverlayManager(overlay);

    // this.wglp = new WebglPlotBundle.WebglPlot(this.canvas, {debug : true});
    // this.wglp.webgl = WebGLDebugUtils.makeDebugContext(this.wglp.webgl);
    this.wglp = new WebglPlotBundle.WebglPlot(this.canvas);

    /* Which channels are selected for plotting. */
    this.states = {};

    /* Point managers for individual channels. */
    this.channels = {};
    this.colors = colors;
    this.rgbaColors = {};

    /* Line objects by channel name. */
    this.lines = {};

    /* Keep track of x-axis bounds for each channel. */
    this.oldestTimestamps = {};
    this.newestTimestamps = {};
    this.minTimestamp = null;
    this.maxTimestamp = null;
  }

  update(time) {
    this.overlay.update(time);
    this.wglp.update();
  }

  clearPoints(name) {
    if (name in this.oldestTimestamps) {
      delete this.oldestTimestamps[name];
    }
    if (name in this.newestTimestamps) {
      delete this.newestTimestamps[name];
    }
    if (name in this.channels) {
      this.channels[name].buffer.reset();
    }
  }

  clearAllPoints() {
    for (const key in this.lines) {
      this.clearPoints(key);
    }
    this.updateAllLines();
  }

  removeLine(name) {
    if (name in this.lines) {
      delete this.lines[name];
    }
  }

  channelState(name, state) {
    this.states[name] = state;

    if (state) {
      this.newLine(name);
    } else {
      this.clearPoints(name);
      this.removeLine(name);
    }

    this.updateLines();
  }

  updateTimeBounds() {
    /* Compute x-axis bounds (min and max timestamps). */
    this.minTimestamp = null;
    this.maxTimestamp = null;

    for (const key in this.oldestTimestamps) {
      let oldest = this.oldestTimestamps[key];
      let newest = this.newestTimestamps[key];
      if (this.minTimestamp == null || oldest < this.minTimestamp) {
        this.minTimestamp = oldest;
      }
      if (this.maxTimestamp == null || newest > this.maxTimestamp) {
        this.maxTimestamp = newest;
      }
    }

    this.overlay.minTimestamp = this.minTimestamp;
    this.overlay.maxTimestamp = this.maxTimestamp;
  }

  drawLines() {
    /* Re-draw all lines. */
    if (this.minTimestamp != null && this.maxTimestamp != null) {
      for (const key in this.channels) {
        if (key in this.lines) {
          this.channels[key].draw(this.lines[key], this.minTimestamp,
                                  this.maxTimestamp);
        }
      }
    }
  }

  handleMessage(data) {
    /* Handle scroll. */
    if ("deltaY" in data) {
      this.updateDepth(data["deltaY"]);
    } else {
      this.overlay.handleMessage(data);
    }
  }

  handlePoints(points) {
    /* Handle ingesting new point data. */
    for (const key in points) {
      if (key in this.states && this.states[key]) {
        /* Add point manager and create line for plotted channel. */
        if (!(key in this.channels)) {
          this.channels[key] = new PointManager(this.overlay.bufferDepth);
        }
        if (key in this.lines) {
          let result = this.channels[key].handlePoints(points[key]);

          /* Update timestamp tracking. */
          this.oldestTimestamps[key] = result[0];
          this.newestTimestamps[key] = result[1];
        }
      }
    }

    /* Update UI. */
    this.updateTimeBounds();
    this.drawLines();
  }

  setColor(key, rgb) {
    this.rgbaColors[key] =
        new WebglPlotBundle.ColorRGBA(rgb.r / 255, rgb.g / 255, rgb.b / 255, 1);
  }

  newLine(key) {
    /* Get color for line. */
    if (!(key in this.rgbaColors)) {
      if (key in this.colors) {
        this.setColor(key, this.colors[key]);
      } else {
        this.setColor(key, {
          r : Math.random() * 255,
          g : Math.random() * 255,
          b : Math.random() * 255
        });
      }
    }

    this.lines[key] =
        new WebglPlotBundle.WebglLine(this.rgbaColors[key], this.canvas.width);
  }

  updateLines() {
    /* Clear and re-add lines. */
    this.wglp.removeAllLines();
    for (let key in this.lines) {
      this.wglp.addLine(this.lines[key]);
    }

    this.drawLines();
  }

  updateAllLines() {
    /* Re-add all lines. */
    for (let key in this.lines) {
      this.newLine(key);
    }
    this.updateLines();
  }

  updateSize() {
    /* Update overlay. */
    this.overlay.updateSize(this.canvas.width, this.canvas.height);

    this.wglp.viewport(0, 0, this.canvas.width, this.canvas.height);
    this.updateAllLines();
  }

  updateDepth(wheelDelta) {
    let capacity = this.overlay.bumpCapacity(wheelDelta > 0);
    for (let name in this.channels) {
      /* Make configurable at some point? */
      this.channels[name].buffer.updateCapacity(capacity);
    }
    this.updateAllLines();
  }
}
