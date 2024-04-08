class ChannelTable {
  constructor(name, table) {
    this.name = name;
    this.table = table;

    /* Create row mapping. */
    this.rows = {};
    this.staleState = {};
    for (let child of this.table.children) {
      this.rows[child.id] = child.querySelector(".channel-value");
    }
  }

  pollStaleness(timestamps, time, threshold) {
    for (let key in this.rows) {
      let isStale = timestamps[key] + threshold < time;

      if (!(key in this.staleState) || this.staleState[key] != isStale) {
        this.staleState[key] = isStale;
        if (isStale) {
          this.rows[key].classList.add("stale");
        } else {
          this.rows[key].classList.remove("stale");
        }
      }
    }
  }

  onmessage(data) {
    for (let key in data) {
      if (key in this.rows) {
        let val = data[key];
        let addSpace = true;

        if (Number.isInteger(val)) {
          /* Handle integer formatting. */
        } else {
          /* Handle floating-point numbers. */
          let checkFloat = Number.parseFloat(val);
          if (!Number.isNaN(checkFloat)) {
            addSpace = checkFloat >= 0;
            val = checkFloat.toFixed(5);
          }
        }

        /*
         * This is here so that a value flapping between positive and negative
         * (minus sign appearing and disappearing) doesn't look bad.
         */
        if (addSpace) {
          val = "&nbsp;" + val;
        }
        this.rows[key].innerHTML = val;
      }
    }
  }
}
