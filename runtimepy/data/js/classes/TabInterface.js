/*
 * Define class for generated code to use (instead of generating so many
 * methods).
 */
class TabInterface {
  constructor(name, _worker) {
    this.name = name;
    this.worker = new WorkerInterface(this.name, _worker);

    /* Relevant elements. */
    this.button = document.getElementById("runtimepy-" + this.name + "-tab");
    this.container = document.getElementById("runtimepy-" + this.name);
    this.logs = this.container.querySelector("#" + this.name + "-logs");

    this.plot = new Plot(
        this.container.querySelector("#" + this.name + "-plot"), this.worker);

    this.message_handlers = [];

    this.button.addEventListener("hidden.bs.tab",
                                 this.hidden_handler.bind(this));
    this.button.addEventListener("shown.bs.tab", this.shown_handler.bind(this));

    tabs[this.name] = this;

    /* Always send a message */
    this.show_state_handlers = [
      (is_shown) => {
        let msg = "tab.hidden";
        if (is_shown) {
          msg = "tab.shown";

          /* Update global reference. */
          shown_tab = this.name;
        }
        this.worker.send({kind : msg});
      },
      this.plot.handle_shown.bind(this.plot)
    ];

    if (bootstrap.Tab.getInstance(this.button)) {
      this.show_state_handler(true);
    }
  }

  log(message) {
    console.log(`(${this.name}) ` + message);
    this.logs.value += message + "\n";
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
