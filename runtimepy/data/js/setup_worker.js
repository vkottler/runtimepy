function worker_config(config) {
  let worker_cfg = {};

  /* Look for connections to establish. */
  let ports = config["config"]["ports"];
  for (let port_idx in ports) {
    let port = ports[port_idx];

    /* This business logic could use some work. */
    if (port["name"].includes("runtimepy_websocket")) {
      if (port["name"].includes("data")) {
        worker_cfg["data"] = "ws://localhost:" + port["port"];
      } else {
        worker_cfg["json"] = "ws://localhost:" + port["port"];
      }
    }
  }

  return worker_cfg;
}

/*
 * Do some heinous sh*t to create a worker from our 'text/js-worker' element.
 */
const worker = new Worker(window.URL.createObjectURL(new Blob(
    Array.prototype.map.call(
        document.querySelectorAll("script[type='text\/js-worker']"),
        (script) => script.textContent,
        ),
    {type : "text/javascript"},
    )));

/*
 * Worker message handler.
 */
function worker_message(event) {
  console.log(`Main thread received: ${event.data}.`);
}
worker.onmessage = worker_message;
