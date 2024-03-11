import_pyodide();

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

const script = `
import js
import js_local
from runtimepy.primitives import create

print(create("uint8"))

# can send messages to main thread
js.postMessage("What's good bud!")

# can access connection and config state
print(js_local.config.config.app)
`;

/* Worker entry. */
async function start(config) {
  /* Run pyodide. */
  let pyodide = await loadPyodide();
  await pyodide.loadPackage("micropip");
  const micropip = pyodide.pyimport("micropip");

  /* Install packages. */
  await micropip.install("runtimepy");

  /* Register namespace for local state. */
  pyodide.registerJsModule(
      "js_local", {config : config, conns : create_connections(config)});

  await pyodide.runPythonAsync(script);
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
