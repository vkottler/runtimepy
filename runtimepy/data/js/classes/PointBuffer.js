class PointBuffer {
  constructor(capacity) {
    /* Only used by initial capacity update. */
    this.values = [];
    this.timestamps = [];

    this.elements = 0;
    this.updateCapacity(capacity);
  }

  reset() {
    this.head = 0;
    this.tail = 0;
    this.elements = 0;
    this.oldestTimestamp = null;
    this.newestTimestamp = null;
  }

  updateCapacity(capacity) {
    /* Copy existing values. */
    let points = [];

    let count = Math.min(this.elements, capacity, this.capacity);
    if (count > 0) {
      let startIdx = this.head;

      /* If the buffer is getting smaller, advance the buffer index forward. */
      if (count < this.elements) {
        startIdx += this.elements - count;
        startIdx = startIdx % this.capacity;
      }

      for (let i = 0; i < count - 1; i++) {
        let idx = (startIdx + i) % this.capacity;
        points.push([ this.values[idx], this.timestamps[idx] ]);
      }
    }

    /* Reset state and re-ingest points. */
    this.reset();
    this.capacity = capacity;
    this.values = new Array(this.capacity);
    this.timestamps = new Array(this.capacity);

    this.ingest(points);
  }

  ingest(points) {
    for (let point of points) {
      /* Store point. */
      this.values[this.tail] = point[0];
      this.timestamps[this.tail] = point[1];

      /* Advance tail. */
      this.tail = this.incrIndex(this.tail);

      /* Keep track of capacity utilization. */
      this.elements = Math.min(this.elements + 1, this.capacity);

      /* Ensure head advances if necessary. */
      if (this.head == this.tail) {
        this.head = this.incrIndex(this.head);
      }
    }

    /* Update tracking of oldest and newest point timestamps. */
    this.oldestTimestamp = this.timestamps[this.head];
    this.newestTimestamp = this.timestamps[this.newestIdx()];
  }

  normalizeTimestamps(newestIdx, oldestIdx, oldestTimestamp, newestTimestamp) {
    /*
     * Determine slope+offset so each timestamp can be mapped to (-1,1)
     * domain.
     */

    let slope = 2 / (newestTimestamp - oldestTimestamp);
    let times = [];

    if (slope > 0) {
      /* Build array of plot-able timestamp X values. */
      let idx = oldestIdx;

      while (idx != newestIdx) {
        times.push(((this.timestamps[idx] - oldestTimestamp) * slope) - 1);
        idx = this.incrIndex(idx);
      }
      times.push(((this.timestamps[idx] - oldestTimestamp) * slope) - 1);

    } else {
      /* need to root-cause this off-by-one issue */
      // console.log(`${newestIdx}, ${oldestIdx}, ${this.elements}`);
      // console.log(slope);

      let idx = oldestIdx;
      while (idx != newestIdx) {
        times.push(oldestTimestamp)
        idx = this.incrIndex(idx);
      }
    }

    return times;
  }

  normalizeValues(newestIdx, oldestIdx) {
    let maxVal = null;
    let minVal = null;

    /* First pass: find current min and max values. */
    let idx = oldestIdx;
    let curr;
    while (idx != newestIdx) {
      curr = this.values[idx];

      if (maxVal == null || curr > maxVal) {
        maxVal = curr;
      }
      if (minVal == null || curr < minVal) {
        minVal = curr;
      }

      idx = this.incrIndex(idx);
    }
    if (maxVal == null || curr > maxVal) {
      maxVal = curr;
    }
    if (minVal == null || curr < minVal) {
      minVal = curr;
    }

    let slope = 2 / (maxVal - minVal);

    /* Second pass: populate normalized data. */
    let values = [];
    idx = oldestIdx;
    while (idx != newestIdx) {
      values.push(((this.values[idx] - minVal) * slope) - 1);
      idx = this.incrIndex(idx);
    }
    values.push(((this.values[idx] - minVal) * slope) - 1);

    return values;
  }

  incrIndex(val) { return (val + 1) % this.capacity; }

  newestIdx() {
    let result = this.tail - 1;
    if (result < 0) {
      result = this.capacity - 1;
    }
    return result;
  }

  draw(line, oldestTimestamp, newestTimestamp) {
    /* Need at least two points to draw a line. */
    if (this.elements < 2) {
      return;
    }

    /* Find indices for oldest and newest points. */
    let oldestIdx = this.head;

    /* Build arrays of plot-able (normalized) timestamps and values. */
    let newestIdx = this.newestIdx();

    let times = this.normalizeTimestamps(newestIdx, oldestIdx, oldestTimestamp,
                                         newestTimestamp);
    let values = this.normalizeValues(newestIdx, oldestIdx);

    /* Set points. */
    let idx = oldestIdx;
    let lineIdx = 0;
    while (idx != newestIdx && lineIdx < line.numPoints) {
      line.setX(lineIdx, times[lineIdx]);
      line.setY(lineIdx, values[lineIdx]);
      idx = this.incrIndex(idx);
      lineIdx++;
    }

    /*
     * Write the last point forward until the line is fully plotted. This has
     * to be done, otherwise there will be lines connecting to (0, 0).
     */
    let lastX = times[lineIdx];
    let lastY = values[lineIdx];
    while (lineIdx < line.numPoints) {
      line.setX(lineIdx, lastX);
      line.setY(lineIdx, lastY);
      lineIdx++;
    }
  }
}
