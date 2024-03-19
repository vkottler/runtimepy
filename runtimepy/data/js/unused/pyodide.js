/* Just an example. */

function import_pyodide() {
  importScripts("https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js");
}

import_pyodide();

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
