/* An array of initialization methods to run. */
let inits = [];

/*
 * Define class for generated code to use (instead of generating so many
 * methods).
 */
class TabInterface {
  constructor(name) {
    this.name = name;
    this.element = document.getElementById("runtimepy-" + this.name + "-tab");
  }

  send_message(data) { worker.postMessage({name : this.name, event : data}); }
}
