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

const plots = new PlotManager();

async function message(data) {
  if ("plot" in data) {
    /* Forward the 'name' field. */
    data["plot"]["name"] = data["name"];
    await plots.handleMessage(data["plot"]);
  } else {
    console.log(`Message for worker:`);
    console.log(data);
  }
}

/* Worker entry. */
async function start(config) {
  console.log(config);

  conns = create_connections(config);

  /* Wait for both connections to be established. */
  for (const key in conns) {
    await conns[key].connected;
  }

  onmessage = async (event) => {
    /* Handle messages meant for this thread. */
    if ("event" in event.data && "worker" in event.data["event"]) {
      /* Forward the 'name' field. */
      event.data["event"]["worker"]["name"] = event.data["name"];
      await message(event.data["event"]["worker"]);
    }
    /* Forward all other messages to the server. */
    else {
      conns["json"].send_json({"ui" : event.data});
    }
  };

  /* Add message handler to forward UI messages to the main thread. */
  conns["json"].message_handlers["ui"] = (data) => {
    /* Handle plot points. */
    for (const key in data) {
      const msg = data[key];
      if ("points" in msg) {
        plots.handlePoints(key, msg["points"]);
      }
    }
    postMessage(data);
  };

  /* Tell main thread we're ready to go. */
  postMessage(0);

  /* Set up the main request-animation-frame loop. */
  function render(time) {
    /* Render plot. */
    plots.render(time);

    /* Keep the server synchronized with frames. */
    conns["json"].send_json({"ui" : {"time" : time}});

    requestAnimationFrame(render);
  }
  requestAnimationFrame(render);
}

/* Handle first message from the main thread. */
onmessage = async (event) => { await start(event.data); };
