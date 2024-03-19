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

function bootstrap_init() {
  /*
   * Enable tooltips.
   * https://getbootstrap.com/docs/5.3/components/tooltips/#overview
   */
  const tooltipTriggerList = document.querySelectorAll(".has-tooltip");
  const tooltipList = [...tooltipTriggerList ].map(
      tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

class App {
  constructor(config, worker) {
    this.config = config;
    this.worker = worker;

    this.config["worker"] = worker_config(this.config);
  }

  async main() {
    /*
     * Run application initialization when the worker thread responds with an
     * expected value.
     */
    worker.addEventListener("message", async (event) => {
      if (event.data == 0) {
        /* Run tab initialization. */
        for await (const init of inits) {
          await init();
        }

        /* Prepare worker message handler. */
        this.worker.onmessage = async (event) => {
          for (const key in event.data) {
            /* Handle forwarding messages to individual tabs. */
            if (key in tabs) {
              tabs[key].onmessage(event.data[key]);
            }
          }
        };
      }
    }, {once : true});

    /* Start worker. */
    this.worker.postMessage(this.config);

    bootstrap_init();
  }
}

/* Load configuration data then run application entry. */
window.onload = async () => {
  await (new App(await (await fetch(window.location.origin + "/json")).json(),
                 worker))
      .main();
};
