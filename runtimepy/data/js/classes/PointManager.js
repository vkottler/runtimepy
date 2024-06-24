class PointManager {
  constructor(initialCapacity) {
    /* How should capacity be controlled? Try to find UI element (probably
     * needs to be passed in). */
    this.buffer = new PointBuffer(initialCapacity);
  }

  draw(line, minTimestamp, maxTimestamp) {
    this.buffer.draw(line, minTimestamp, maxTimestamp);
  }

  handlePoints(points) {
    this.buffer.ingest(points);
    return [ this.buffer.oldestTimestamp, this.buffer.newestTimestamp ];
  }
}
