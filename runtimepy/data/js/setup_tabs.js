/* An array of initialization methods to run. */
let inits = [];
let tabs = {};

/*
 * Define class for generated code to use (instead of generating so many
 * methods).
 */
class TabInterface {
  constructor(name, _worker) {
    this.name = name;
    this.worker = _worker;

    this.element = document.getElementById("runtimepy-" + this.name + "-tab");

    this.message_handlers = [];

    this.element.addEventListener("hidden.bs.tab",
                                  this.hidden_handler.bind(this));
    this.element.addEventListener("shown.bs.tab",
                                  this.shown_handler.bind(this));

    tabs[this.name] = this;

    if (bootstrap.Tab.getInstance(this.element)) {
      this.shown_handler();
    }
  }

  send_message(data) {
    this.worker.postMessage({name : this.name, event : data});
  }

  shown_handler() { this.send_message({kind : "tab.shown"}); }

  hidden_handler() { this.send_message({kind : "tab.hidden"}); }

  onmessage(data) {
    for (const handler of this.message_handlers) {
      handler(data);
    }
  }
}
