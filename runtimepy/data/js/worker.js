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

  conns = create_connections(config);

  /* Wait for both connections to be established. */
  for (const key in conns) {
    await conns[key].connected;
  }

  /* Forward all other messages to the server. */
  onmessage = async (event) => { conns["json"].send_json({"ui" : event.data}); }

  /* Tell main thread we're ready to go. */
  postMessage(0);
}

/* Handle first message from the main thread. */
onmessage = async (event) => { await start(event.data); };
