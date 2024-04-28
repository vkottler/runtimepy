class PlotDrawer {
  constructor(canvas) {
    this.canvas = canvas;
    this.wglp = new WebglPlotBundle.WebglPlot(this.canvas);

    /* Which channels are selected for plotting. */
    this.states = {};

    /* need to make this an N entity for multiple channels */
    this.line = null;
  }

  update() {
    /* handle all new points */

    const freq = 0.001;
    const amp = 0.5;
    const noise = 0.1;

    for (let i = 0; i < this.line.numPoints; i++) {
      const ySin = Math.sin(Math.PI * i * freq * Math.PI * 2);
      const yNoise = Math.random() - 0.5;
      this.line.setY(i, ySin * amp + yNoise * noise);
    }

    this.wglp.update();
  }

  channelState(name, state) { this.states[name] = state; }

  handlePoints(points) {
    for (const key in points) {
      if (key in this.states && this.states[key]) {
        /* Handle updating line data. */
        console.log(key);
        console.log(points[key]);
      }
    }
  }

  updateSize() {
    /* is this the demo? */
    const color = new WebglPlotBundle.ColorRGBA(Math.random(), Math.random(),
                                                Math.random(), 1);

    this.line = new WebglPlotBundle.WebglLine(color, this.canvas.width);
    this.line.arrangeX();
    this.wglp.removeAllLines();
    this.wglp.addLine(this.line);

    this.wglp.viewport(0, 0, this.canvas.width, this.canvas.height);
  }
}
