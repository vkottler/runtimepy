function create_connections(config) {
  /* This business logic could use some work. */
  const conn_factories = {"json" : JsonConnection, "data" : DataConnection};

  let worker_cfg = config["worker"];
  let conns = {};
  for (let name in conn_factories) {
    conns[name] = new conn_factories[name](name, worker_cfg[name]);
  }

  return conns;
}

/* Worker entry. */
async function start(config) {
  console.log(config);

  let conns = create_connections(config);
}

started = false;

/* Handle messages from the main thread. */
onmessage = async (event) => {
  /* First message.*/
  if (!started) {
    await start(event.data);
    started = true;
  } else {
    /* Additional messages not handled. */
    console.log("MESSAGE NOT HANDLED.");
    console.log(event.data);
  }
};
