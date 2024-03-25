/*
 * Define class for generated code to use (instead of generating so many
 * methods).
 */
class TabInterface {
  constructor(name, _worker) {
    this.name = name;
    this.worker = new WorkerInterface(this.name, _worker);

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
      }
      this.worker.send({kind : msg});

      /* Could remove this. */
      this.log(msg);
    } ];

    /* Plot related. */
    let plot = this.query("#" + this.name + "-plot");
    if (plot) {
      this.plot = new Plot(plot, this.worker);
      this.show_state_handlers.push(this.plot.handle_shown.bind(this.plot));
    }

    this.initButton();
  }

  query(data) { return this.container.querySelector(data); }

  initButton() {
    let button = document.getElementById("runtimepy-" + this.name + "-tab");
    button.addEventListener("hidden.bs.tab", this.hidden_handler.bind(this));
    button.addEventListener("shown.bs.tab", this.shown_handler.bind(this));
    if (bootstrap.Tab.getInstance(button)) {
      this.show_state_handler(true);
    }
  }

  log(message) {
    console.log(`(${this.name}) ` + message);
    if (this.logs) {
      this.logs.value += message + "\n";
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
    for (const handler of this.message_handlers) {
      handler(data);
    }
  }
}
