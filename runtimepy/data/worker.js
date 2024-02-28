onmessage = (event) => {
  console.log(event);
  postMessage("Hello, world!");
};

console.log("Worker thread!");
