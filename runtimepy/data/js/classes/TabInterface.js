const staleMs = 500;

/*
 * Define class for generated code to use (instead of generating so many
 * methods).
 */
class TabInterface {
  constructor(name, _worker) {
    this.name = name;
    this.queryName = CSS.escape(this.name);

    this.worker = new WorkerInterface(this.name, _worker);

    /* Send an initialization message. */
    this.worker.send({kind : "init"});

    /* Relevant elements. */
    this.container = document.getElementById(`runtimepy-${this.name}`);
    this.logs = this.query(`#${this.queryName}-logs`);

    this.message_handlers = [];

    tabs[this.name] = this;

    /* Channel-table manager. */
    this.channels = undefined;
    this.channelsPending = {};
    this.time = 0;
    this.channelTimestamps = {};
    this.channelColorButtons = {};

    let table = this.query("tbody");
    if (table) {
      this.channels = new ChannelTable(this.name, table, this.worker);
    }

    /* Always send a message */
    this.show_state_handlers = [ (is_shown) => {
      let msg = "tab.hidden";
      if (is_shown) {
        msg = "tab.shown";

        /* Update global reference. */
        shown_tab = this.name;
        hash.setTab(shown_tab);
      }
      this.worker.send({kind : msg});
    } ];

    this.initPlot();
    this.initCommand();
    this.initControls();
    this.initButton();
  }

  initCommand() {
    let command = this.query(`#${this.queryName}-command`);
    if (command) {
      command.onkeypress = (event) => {
        if (event.key == "Enter") {
          let cmd = event.target.value.trim();

          if (cmd == "cls" || cmd == "clear") {
            this.clearLog();
            this.clearPlotPoints();
          } else {
            this.worker.command(cmd);
          }

          event.target.value = "";
        }
      };
    }
  }

  updateChannelStyles(pattern) {
    hash.handleChannelFilter(this.name, pattern);

    if (!pattern) {
      pattern = ".*";
    }
    const re = new RegExp(pattern);

    for (let [name, elem] of Object.entries(this.channelRows)) {
      if (re.test(name)) {
        elem.style.display = "table-row";
      } else {
        elem.style.display = "none";
      }
    }
  }

  channelKeydown(event) {
    if (event.key == "Enter") {
      this.channelFilter.value = "";
      this.updateChannelStyles(this.channelFilter.value);
    } else {
      let curr = this.channelFilter.value;
      if (event.key == "Backspace") {
        curr = curr.slice(0, -1);
      } else {
        curr += event.key;
      }

      this.updateChannelStyles(curr);
    }
  }

  initControls() {
    /* Initialize channel filter. */
    this.channelFilter = this.query("#channel-filter");
    this.channelRows = {};
    if (this.channelFilter) {
      for (let row of this.queryAll("tr.channel-row")) {
        this.channelRows[row.id] = row;
      }

      this.channelFilter.addEventListener("keydown",
                                          this.channelKeydown.bind(this));
    }

    /* Initialize enumeration command drop downs. */
    for (let enums of this.queryAll("td>select")) {
      enums.onchange = this.setHandler(enums);
    }

    /* Initialize toggle buttons. */
    for (let toggle of this.queryAll("td>button.toggle-value")) {
      toggle.onclick =
          (() => { this.worker.command(`toggle ${toggle.id}`); }).bind(this);
    }

    /* Initialize channel table and plot divider. */
    let divider = this.query(".vertical-divider");
    if (divider) {
      this.setupVerticalDivider(divider);
    }

    /* Initialize sliders. */
    for (let slider of this.queryAll(".slider")) {
      setupCursorContext(slider, this.setupSliderEvents.bind(this));
      if (this.channels) {
        this.channels.sliders[slider.id] = slider;
      }
    }

    /* Initialize return-to-default. */
    let defaultButtons = [];
    for (let elem of this.queryAll(".default-button")) {
      elem.onclick = this.setHandler(elem);
      defaultButtons.push(elem);
    }

    /* Initialize a global return-to-default button if one exists. */
    let elem = this.query("#set-defaults");
    if (elem) {
      elem.onclick = () => {
        for (let button of defaultButtons) {
          button.click();
        }
      };
    }

    /* Initialize custom-command sending interfaces. */
    let selector = this.query("#custom-commands");
    let send = this.query("#send-custom-commands");
    if (selector && send) {
      send.onclick = () => { this.worker.command(`custom ${selector.value}`); };
    }
  }

  setHandler(elem) {
    let handler =
        () => { this.worker.command(`set ${elem.id} ${elem.value}`); };
    return handler.bind(this);
  }

  setupSliderEvents(elem, down, move, up) {
    setupCursorMove(elem, down, move, up, this.setHandler(elem));
  }

  setupVerticalDividerEvents(elem, down, move, up) {
    elem.addEventListener(down, (event) => {
      let elem = this.query(".channel-column");

      let origX = event.clientX || event.touches[0].clientX;

      /* Track mouse movement while the mouse is held down. */
      let handleMouse = (event) => {
        let eventX = event.clientX || event.touches[0].clientX;

        let deltaX = origX - eventX;
        elem.style.width = elem.getBoundingClientRect().width - deltaX + "px";
        origX = eventX;
      };
      document.addEventListener(move, handleMouse);

      /* Remove mouse handler on mouse release. */
      document.addEventListener(
          up, (event) => { document.removeEventListener(move, handleMouse); },
          {once : true});
    });
  }

  setupVerticalDivider(elem) {
    setupCursorContext(elem, this.setupVerticalDividerEvents.bind(this));
  }

  initPlot() {
    let plot = this.query(`#${this.queryName}-plot`);
    if (plot) {
      this.plot =
          new Plot(plot, this.worker, this.query(`#${this.queryName}-overlay`));
      this.show_state_handlers.push(this.plot.handle_shown.bind(this.plot));

      /* Initialize plot-channel buttons. */
      for (let elem of this.queryAll("input.form-check-input")) {
        let chan = elem.id.split("-")[1];

        /* Store a reference to the plot button. */
        let lineColorButton =
            this.query("#" + CSS.escape(chan) + "-line-color");
        if (lineColorButton) {
          this.channelColorButtons[chan] = lineColorButton;
          lineColorButton.onclick = ((event) => {
                                      let color = randomHexColor();
                                      lineColorButton.style.color = color;
                                      this.sendPlotChannelColor(chan, color);
                                    }).bind(this);
        }

        elem.addEventListener(
            "change", ((event) => {
                        let state = elem.checked;

                        hash.handlePlotChannelToggle(this.name, chan, state);
                        this.sendPlotChannelState(chan, state);

                        if (chan in this.channelColorButtons) {
                          let elem = this.channelColorButtons[chan];
                          if (state) {
                            /* Show button and set a color for this line. */
                            elem.classList.remove("d-none");
                            elem.click();
                          } else {
                            /* Hide button. */
                            elem.classList.add("d-none");
                          }
                        }
                      }).bind(this));
      }

      /* Initialize plotted-channel clearing interface. */
      let elem = this.query("#clear-plotted-channels");
      if (elem) {
        elem.onclick =
            (() => { hash.clearPlotChannels(this.name); }).bind(this);
      }

      /* Initialize plotted-point clearing interface. */
      elem = this.query("#clear-plotted-points");
      if (elem) {
        elem.onclick = this.clearPlotPoints.bind(this);
      }
    }
  }

  clearPlotPoints() { this.worker.toWorker({"plot" : {"clear" : true}}); }

  sendPlotChannelColor(chan, color) {
    this.worker.toWorker({"plot" : {"channel" : chan, "color" : color}});
  }

  sendPlotChannelState(chan, state) {
    let msg = {"channel" : chan, "state" : state};
    this.worker.toWorker({"plot" : msg});
    this.worker.send({kind : "plot", value : msg});
  }

  query(data) { return this.container.querySelector(data); }
  queryAll(data) { return this.container.querySelectorAll(data); }

  initButton() {
    this.tabButton = document.getElementById("runtimepy-" + this.name + "-tab");
    this.tabButton.addEventListener("hidden.bs.tab",
                                    this.hidden_handler.bind(this));
    this.tabButton.addEventListener("shown.bs.tab",
                                    this.shown_handler.bind(this));

    if (bootstrap.Tab.getInstance(this.tabButton)) {
      this.show_state_handler(true);
    }
  }

  isShown() { return shown_tab == this.name; }

  log(message) {
    if (this.logs) {
      this.logs.value += message + "\n";
      if (this.isShown()) {
        this.logs.scrollTo(0, this.logs.scrollHeight);
      }
    }
  }

  clearLog() {
    if (this.logs) {
      this.logs.value = "";
      this.logs.scrollTo(0, 0);
    }
  }

  show_state_handler(is_shown) {
    for (const handler of this.show_state_handlers) {
      handler(is_shown);
    }
  }

  shown_handler() { this.show_state_handler(true); }

  hidden_handler() { this.show_state_handler(false); }

  onmessage(data) {
    /* Handle log messages. */
    if ("log_message" in data) {
      this.log(data["log_message"]);
    }
    if ("log_messages" in data) {
      for (let msg of data["log_messages"]) {
        this.log(msg);
      }
    }

    /* Handle data points. */
    if ("points" in data) {
      for (let key in data["points"]) {
        let points = data["points"][key];

        /* Update channel-table tracking based on most recent point only. */
        this.channelsPending[key] = points[points.length - 1][0];
        this.channelTimestamps[key] = this.time;
      }
    }

    /* Handle actions. */
    if ("actions" in data) {
      for (let action of data["actions"]) {
        switch (action) {
        case "clear_points":
          this.clearPlotPoints();
          break;
        default:
          console.log(`Action '${action}' not hangled!`);
          break;
        }
      }
    }

    /* Stage any channel-table re-paints. */
    if (this.channels) {
      for (let key in data) {
        if (key in this.channels.rows) {
          this.channelsPending[key] = data[key];
          this.channelTimestamps[key] = this.time;
        }
      }
    }

    for (const handler of this.message_handlers) {
      handler(data);
    }
  }

  poll(time) {
    this.time = time;

    if (this.channels && this.isShown()) {
      /* Update channel values. */
      if (this.channelsPending) {
        this.channels.onmessage(this.channelsPending);
        this.channelsPending = {};
      }

      /* Poll staleness. */
      this.channels.pollStaleness(this.channelTimestamps, this.time, staleMs);
    }
  }
}
