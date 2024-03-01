function get_config() {
  const config = {};

  /* Add connection information to configuration object. */
  const elems = [ "http_url", "websocket_json_url", "websocket_data_url" ];
  for (let idx in elems) {
    let elem = elems[idx];
    config[elem] = document.getElementById(elem).innerText;
  }

  return config;
}
