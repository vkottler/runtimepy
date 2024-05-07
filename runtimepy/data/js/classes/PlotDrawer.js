class PlotDrawer {
  constructor(canvas) {
    this.canvas = canvas;

    // this.wglp = new WebglPlotBundle.WebglPlot(this.canvas, {debug : true});
    // this.wglp.webgl = WebGLDebugUtils.makeDebugContext(this.wglp.webgl);
    this.wglp = new WebglPlotBundle.WebglPlot(this.canvas);

    /* Which channels are selected for plotting. */
    this.states = {};

    /* Point managers for individual channels. */
    this.channels = {};

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

  newLine(key) {
    /* Random color. */
    const color = new WebglPlotBundle.ColorRGBA(Math.random(), Math.random(),
                                                Math.random(), 1);
    this.lines[key] = new WebglPlotBundle.WebglLine(color, this.canvas.width);

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

  updateSize() {
    /* Re-add all lines. */
    for (let key in this.lines) {
      this.newLine(key);
    }
    this.updateLines();

    this.wglp.viewport(0, 0, this.canvas.width, this.canvas.height);
  }
}
