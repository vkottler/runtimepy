class PointManager {
  constructor() {
    this.color = new WebglPlotBundle.ColorRGBA(Math.random(), Math.random(),
                                               Math.random(), 1);

    /* How should capacity be controlled? */
    this.buffer = new PointBuffer(256);
  }

  draw(line) { this.buffer.draw(line); }

  handlePoints(points, line) { this.buffer.ingest(points, line); }
}
