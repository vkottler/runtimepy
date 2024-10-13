function worker_config(config) {
  let worker_cfg = {};

  let port_name = "runtimepy_websocket";
  let uri_prefix = "ws";

  /* Ensured TLS is handled properly. */
  if (location.protocol.includes("https")) {
    port_name = "runtimepy_secure_websocket";
    uri_prefix += "s";
  }

  /* Look for connections to establish. */
  let ports = config["config"]["ports"];
  for (let port_idx in ports) {
    let port = ports[port_idx];

    /* Load from configuration data if provided. */
    let hostname =
        config["config"]["websocket_hostname"] || window.location.hostname;

    /* This business logic could use some work. */
    if (port["name"].includes(port_name)) {
      if (port["name"].includes("data")) {
        worker_cfg["data"] = `${uri_prefix}://${hostname}:` + port["port"];
      } else {
        worker_cfg["json"] = `${uri_prefix}://${hostname}:` + port["port"];
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
