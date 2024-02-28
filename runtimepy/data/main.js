const blob = new Blob(
  Array.prototype.map.call(
    document.querySelectorAll("script[type='text\/js-worker']"),
    (script) => script.textContent,
  ),
  { type: "text/javascript" },
);

// Creating a new document.worker property containing all our "text/js-worker" scripts.
document.worker = new Worker(window.URL.createObjectURL(blob));

document.worker.onmessage = (event) => {
  pageLog(`Received: ${event.data}`);
};

// Start the worker.
window.onload = () => {
  document.worker.postMessage("");
};

console.log("Main thread!");
