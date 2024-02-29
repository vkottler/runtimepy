const blob = new Blob(
  Array.prototype.map.call(
    document.querySelectorAll("script[type='text\/js-worker']"),
    (script) => script.textContent,
  ),
  { type: "text/javascript" },
);

// Creating a new document.worker property containing all our "text/js-worker"
// scripts.
let worker = new Worker(window.URL.createObjectURL(blob));

worker.onmessage = (event) => {
  console.log(`Main thread received: ${event.data}.`);
};

// Start the worker.
window.onload = () => {
  worker.postMessage("Message from main thread.");
};

console.log("Main thread!");
