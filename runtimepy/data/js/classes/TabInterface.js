/*
 * Define class for generated code to use (instead of generating so many
 * methods).
 */
class TabInterface {
  constructor(name, _worker) {
    this.name = name;
    this.worker = new WorkerInterface(this.name, _worker);

    /* Send an initialization message. */
    this.worker.send({kind : "init"});

    /* Relevant elements. */
    this.container = document.getElementById("runtimepy-" + this.name);
    this.logs = this.query("#" + this.name + "-logs");

    this.message_handlers = [];

    tabs[this.name] = this;

    /* Always send a message */
    this.show_state_handlers = [ (is_shown) => {
      let msg = "tab.hidden";
      if (is_shown) {
        msg = "tab.shown";

        /* Update global reference. */
        shown_tab = this.name;
        hash.setTab(shown_tab);

        //
        console.log($(this.container).find(".ui-widget-content"));
        console.log("WTF");

        $(this.container).find(".ui-widget-content").resizable({handles : "e"});
      }
      this.worker.send({kind : msg});
    } ];

    this.initPlot();
    this.initCommand();
    this.initControls();
    this.initButton();
  }

  initCommand() {
    let command = this.query("#" + this.name + "-command")
    if (command) {
      command.onkeypress = (event) => {
        if (event.key == "Enter") {
          let cmd = event.target.value.trim();

          if (cmd == "cls" || cmd == "clear") {
            this.clearLog();
          } else {
            this.command(cmd);
          }

          event.target.value = "";
        }
      };
    }
  }

  command(data) { this.worker.send({kind : "command", value : data}); }

  updateChannelStyles(pattern) {
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
    for (let enums of this.queryAll("select")) {
      enums.onchange =
          (() => { this.command(`set ${enums.id} ${enums.value}`); })
              .bind(this);
    }

    /* Initialize toggle buttons. */
    for (let toggle of this.queryAll("td>button")) {
      toggle.onclick =
          (() => { this.command(`toggle ${toggle.id}`); }).bind(this);
    }
  }

  initPlot() {
    let plot = this.query("#" + this.name + "-plot");
    if (plot) {
      this.plot = new Plot(plot, this.worker);
      this.show_state_handlers.push(this.plot.handle_shown.bind(this.plot));
    }
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

  log(message) {
    if (this.logs) {
      this.logs.value += message + "\n";
    }
  }

  clearLog() { this.logs.value = ""; }

  show_state_handler(is_shown) {
    for (const handler of this.show_state_handlers) {
      handler(is_shown);
    }
  }

  shown_handler() { this.show_state_handler(true); }

  hidden_handler() { this.show_state_handler(false); }

  onmessage(data) {
    if ("log_message" in data) {
      this.log(data["log_message"]);
    }

    for (const handler of this.message_handlers) {
      handler(data);
    }
  }
}
