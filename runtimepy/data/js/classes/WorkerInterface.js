class WorkerInterface {
  constructor(name, _worker) {
    this.name = name;
    this.worker = _worker;
  }

  send(data, param) {
    this.worker.postMessage({name : this.name, event : data}, param);
  }

  toWorker(data, param) { return this.send({"worker" : data}, param); }
}
