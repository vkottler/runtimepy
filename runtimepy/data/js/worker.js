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

started = false;

let conns;

/* Worker entry. */
async function start(config) {
  console.log(config);

  conns = create_connections(config);

  /* Wait for both connections to be established. */

  /* Tell main thread we're ready to go. */
  postMessage(0);
}

/* Handle messages from the main thread. */
onmessage = async (event) => {
  /* First message.*/
  if (!started) {
    await start(event.data);
    started = true;
  } else {
    console.log(`Worker thread received: ${event.data}.`);

    /* Need to make this actually work. */
    // conns["json"].send_json({"ui" : event.data});
  }
};
