class PlotDrawer {
  constructor(canvas, colors) {
    this.canvas = canvas;

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
  }

  update() { this.wglp.update(); }

  channelState(name, state) {
    this.states[name] = state;

    if (state) {
      this.newLine(name);
    } else {
      delete this.lines[name];
      delete this.oldestTimestamps[name];
      delete this.newestTimestamps[name];
      this.channels[name].buffer.reset();
    }

    this.updateLines();
  }

  handlePoints(points) {
    /* Handle ingesting new point data. */
    for (const key in points) {
      if (key in this.states && this.states[key]) {
        /* Add point manager and create line for plotted channel. */
        if (!(key in this.channels)) {
          this.channels[key] = new PointManager();
        }
        if (key in this.lines) {
          let result = this.channels[key].handlePoints(points[key]);

          /* Update timestamp tracking. */
          this.oldestTimestamps[key] = result[0];
          this.newestTimestamps[key] = result[1];
        }
      }
    }

    /* Compute x-axis bounds (min and max timestamps). */
    let minTimestamp = null;
    let maxTimestamp = null;
    for (const key in this.oldestTimestamps) {
      let oldest = this.oldestTimestamps[key];
      let newest = this.newestTimestamps[key];
      if (minTimestamp == null || oldest < minTimestamp) {
        minTimestamp = oldest;
      }
      if (maxTimestamp == null || newest > maxTimestamp) {
        maxTimestamp = newest;
      }
    }

    /* Re-draw all lines. */
    if (minTimestamp != null && maxTimestamp != null) {
      for (const key in this.channels) {
        if (key in this.lines) {
          this.channels[key].draw(this.lines[key], minTimestamp, maxTimestamp);
        }
      }
    }
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

    if (key in this.channels) {
      this.channels[key].draw(this.lines[key]);
    }
  }

  updateLines() {
    /* Clear lines. */
    this.wglp.removeAllLines();

    /* Put lines back. */
    for (let key in this.lines) {
      this.wglp.addLine(this.lines[key]);
    }
  }

  updateAllLines() {
    /* Re-add all lines. */
    for (let key in this.lines) {
      this.newLine(key);
    }
    this.updateLines();
  }

  updateSize() {
    this.updateAllLines();
    this.wglp.viewport(0, 0, this.canvas.width, this.canvas.height);
  }

  updateDepth(wheelDelta) {
    for (let name in this.channels) {
      let chan = this.channels[name];

      /* Make configurable at some point? */
      chan.buffer.bumpCapacity(wheelDelta < 0);

      chan.draw(this.lines[name]);
    }
  }
}
