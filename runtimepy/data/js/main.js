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

  /* Initialize tab filter. */
  let tabs = document.getElementById("runtimepy-tabs");
  if (tabs) {
    const tabFilter = new TabFilter(tabs);
  }
}

/* Load configuration data then run application entry. */
window.onload = async () => {
  await (new App(await (await fetch(window.location.origin + "/json")).json(),
                 worker))
      .main();
};
