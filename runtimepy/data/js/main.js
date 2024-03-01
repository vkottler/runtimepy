function worker_message(event) {
  console.log(`Main thread received: ${event.data}.`);
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
worker.onmessage = worker_message;

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

function main(config) {
  /* Send configuration data to the worker. */
  config["worker"] = worker_config(config);
  worker.postMessage(config);

  /* Canvas. */
  // let ctx = document.getElementById("canvas").getContext("2d");
  // ctx.lineWidth = 10;
  // ctx.strokeRect(20, 20, 40, 40);
}

/* Load configuration data then run application entry. */
window.onload = () => {
  fetch(window.location.origin + "/json")
      .then((value) => { return value.json(); })
      .then((value) => { main(value); });
};
