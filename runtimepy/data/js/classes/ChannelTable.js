class ChannelTable {
  constructor(name, table, worker) {
    this.name = name;
    this.table = table;
    this.worker = worker;

    /* Create row mapping. */
    this.rows = {};
    this.staleState = {};
    for (let child of this.table.children) {
      this.rows[child.id] = child.querySelector(".channel-value");
    }

    /* A mapping of channel names to a possible slider element (populated
     * externally). */
    this.sliders = {};

    /* Initialize input boxes. */
    this.channelInputs = {};
    for (let input of table.querySelectorAll("input.channel-value-input")) {
      this.channelInputs[input.id] = input;

      let cmd =

          /* Register handler for pressing enter. */
          input.onkeypress = (event) => {
            if (event.key == "Enter") {
              this.worker.command(`set ${input.id} ${input.value}`);
            }
          };

      /* Register handler for pressing send button. */
      input.nextElementSibling.onclick =
          (event) => { this.worker.command(`set ${input.id} ${input.value}`); };
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

        /* Update input box if one exists. */
        if (key in this.channelInputs) {
          this.channelInputs[key].value = val;
        }

        /* Update slider if one exists. */
        if (key in this.sliders) {
          let elem = this.sliders[key];
          if (!elem.classList.contains("moving")) {
            elem.value = val;
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
