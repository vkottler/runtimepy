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

    /* need to make this an N entity for multiple channels */
    this.lines = {};
  }

  update() { this.wglp.update(); }

  channelState(name, state) {
    this.states[name] = state;

    if (state) {
      this.newLine(name);
    } else {
      delete this.lines[name];
    }

    this.updateLines();
  }

  handlePoints(points) {
    for (const key in points) {
      if (key in this.states && this.states[key]) {
        /* Add point manager and create line for plotted channel. */
        if (!(key in this.channels)) {
          this.channels[key] = new PointManager();
        }
        if (key in this.lines) {
          this.channels[key].handlePoints(points[key], this.lines[key]);
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
