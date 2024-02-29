onmessage = (event) => {
  console.log(event);
  postMessage("Worker received message!");
};

console.log("Worker thread!");
