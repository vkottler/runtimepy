function worker_config(config) {
  let worker_cfg = {};

  /* Look for connections to establish. */
  let ports = config["config"]["ports"];
  for (let port_idx in ports) {
    let port = ports[port_idx];

    /* Load from configuration data at some point? */
    let hostname = window.location.hostname;

    /* This business logic could use some work. */
    if (port["name"].includes("runtimepy_websocket")) {
      if (port["name"].includes("data")) {
        worker_cfg["data"] = "ws://" + hostname + ":" + port["port"];
      } else {
        worker_cfg["json"] = "ws://" + hostname + ":" + port["port"];
      }
    }
  }

  return worker_cfg;
}

let tabFilter = undefined;

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
    tabFilter = new TabFilter(tabs);
  }
}
