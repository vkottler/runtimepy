class App {
  constructor(config, worker) {
    this.config = config;
    this.worker = worker;

    this.config["worker"] = worker_config(this.config);
  }

  switchTab(newTabName) {
    if (newTabName in tabs && shown_tab != newTabName) {
      tabs[newTabName].tabButton.click();
    }
  }

  async main() {
    /*
     * Run application initialization when the worker thread responds with an
     * expected value.
     */
    worker.addEventListener("message", async (event) => {
      if (event.data == 0) {
        /* Run tab initialization. */
        for await (const init of inits) {
          await init();
        }

        /* Switch tabs if necessary. */
        if (hash.original) {
          this.switchTab(hash.original);
        }

        /* Prepare worker message handler. */
        this.worker.onmessage = async (event) => {
          for (const key in event.data) {
            /* Handle forwarding messages to individual tabs. */
            if (key in tabs) {
              tabs[key].onmessage(event.data[key]);
            }
          }
        };
      }
    }, {once : true});

    /* Start worker. */
    this.worker.postMessage(this.config);

    bootstrap_init();
  }
}
