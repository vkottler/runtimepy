class PointBuffer {
  constructor(capacity) {
    /* Only used by initial capacity update. */
    this.values = [];
    this.timestamps = [];

    this.updateCapacity(capacity);
  }

  reset() {
    this.head = 0;
    this.tail = 0;
    this.elements = 0;
  }

  updateCapacity(capacity) {
    this.capacity = capacity;
    this.reset();

    let newValues = new Array(this.capacity);
    let newTimestamps = new Array(this.capacity);

    /* Copy existing values. */
    for (let i = this.values.length; i < this.capacity; i++) {
      newValues[i] = this.values[i];
      newTimestamps[i] = this.timestamps[i];
    }

    this.values = newValues;
    this.timestamps = newTimestamps;
  }

  ingest(points, line) {
    for (let point of points) {
      /* Store point. */
      this.values[this.tail] = point[0];
      this.timestamps[this.tail] = point[1];

      /* Advance tail. */
      this.tail = (this.tail + 1) % this.capacity;

      /* Keep track of capacity utilization. */
      this.elements = Math.min(this.elements + 1, this.capacity);

      /* Ensure head advances if necessary. */
      if (this.head == this.tail) {
        this.head = (this.head + 1) % this.capacity;
      }
    }

    this.draw(line);
  }

  draw(line) {
    if (this.elements < 2) {
      return;
    }

    /* Find indices for oldest and newest points. */
    let oldestIdx = this.head;
    let newestIdx = this.tail - 1;
    if (newestIdx < 0) {
      newestIdx = this.capacity - 1;
    }

    /*
     * Determine slope+offset so each timestamp can be mapped to (-1,1)
     * domain.
     */
    let oldestTimestamp = this.timestamps[oldestIdx];
    let delta = this.timestamps[newestIdx] - oldestTimestamp;
    let slope = 2 / delta;

    /*
     * Determine slope+offset so each value can be mapped to (-1,1).
     */

    /* Build array of plot-able timestamp X values. */
    let times = [];
    let idx = oldestIdx;
    while (idx != newestIdx) {
      times.push(((this.timestamps[idx] - oldestTimestamp) * slope) - 1);
      idx = (idx + 1) % this.capacity;
    }
    times.push(((this.timestamps[idx] - oldestTimestamp) * slope) - 1);

    /* Set points. */
    idx = oldestIdx;
    let lineIdx = 0;
    while (idx != newestIdx && lineIdx < line.numPoints) {
      line.setX(lineIdx, times[lineIdx]);

      /* Need to use real values. */
      line.setY(lineIdx, (2 * Math.random()) - 1);
      // line.setY(lineIdx, this.values[idx]);

      idx = (idx + 1) % this.capacity;
      lineIdx++;
    }

    /* Write the last point forward until the line is fully plotted. */
    let lastX = times[lineIdx];

    /* Need to use real values. */
    let lastY = (2 * Math.random()) - 1;
    // let lastY = this.values[idx];

    while (lineIdx < line.numPoints) {
      line.setX(lineIdx, lastX);
      line.setY(lineIdx, lastY);
      lineIdx++;
    }
  }
}
