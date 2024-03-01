const conn_factories = {
  "websocket_json_url" : JsonConnection,
  "websocket_data_url" : DataConnection
};

/* Worker entry. */
function start(config) {
  let conns = {};
  for (let name in conn_factories) {
    conns[name] = new conn_factories[name](config[name]);
  }
}

started = false;

/* Handle messages from the main thread. */
onmessage = (event) => {
  /* First message.*/
  if (!started) {
    start(event.data);
    started = true;
  } else {
    /* Additional messages not handled. */
    console.log(event.data);
  }
};
