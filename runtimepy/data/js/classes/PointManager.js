class PointManager {
  constructor() {
    this.maxPoints = 10;
    this.color = new WebglPlotBundle.ColorRGBA(Math.random(), Math.random(),
                                               Math.random(), 1);
    this.reset();
  }

  reset() {
    this.index = 0;
    this.start = null;
  }

  handlePoints(points, line) {
    /* Ingest points (handle circular buffering at some point). */

    let xStep = 2 / line.numPoints;
    let xStart = -1;

    /*

    if (this.start == null) {
      this.start = points[0][1];
    }

    for (let point of points) {
      let i = this.index % line.numPoints;
      line.setY(i, point[0]);
      line.setX(i, xStart + (xStep * this.index));

      this.index++;
    }
    */

    /* DEMO START */

    const freq = 0.001;
    const amp = 0.5;
    const noise = 0.1;

    let i = this.index % line.numPoints;

    const ySin = Math.sin(Math.PI * i * freq * Math.PI * 2);
    const yNoise = Math.random() - 0.5;
    line.setY(i, ySin * amp + yNoise * noise);
    line.setX(i, xStart + (xStep * i));

    this.index++;

    /*
    for (let i = 0; i < line.numPoints; i++) {
      const ySin = Math.sin(Math.PI * i * freq * Math.PI * 2);
      const yNoise = Math.random() - 0.5;
      line.setY(i, ySin * amp + yNoise * noise);
      line.setX(i, xStart + (xStep * i));
    }
    */

    /* DEMO END */
  }
}
