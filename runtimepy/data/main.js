let blob = new Blob(
    Array.prototype.map.call(
        document.querySelectorAll("script[type='text\/js-worker']"),
        (script) => script.textContent,
        ),
    {type : "text/javascript"},
);

// Creating a new document.worker property containing all our "text/js-worker"
// scripts.
let worker = new Worker(window.URL.createObjectURL(blob));

worker.onmessage =
    (event) => { console.log(`Main thread received: ${event.data}.`); };

// Start the worker.
window.onload = () => {
  const config = {
    "http_url" : document.getElementById("http_server_url").innerText,
    "websocket_url" : document.getElementById("websocket_server_url").innerText,
  };

  /* Send configuration data. */
  worker.postMessage(config);
};
