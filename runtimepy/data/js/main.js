/*
 * Application entry.
 */
async function main(config) {
  /* Send configuration data to the worker. */
  config["worker"] = worker_config(config);
  worker.postMessage(config);

  /* Run tab initialization. */
  for await (const init of inits) {
    await init();
  }
}

/* Load configuration data then run application entry. */
window.onload = async () => {
  await main(await (await fetch(window.location.origin + "/json")).json());
};
