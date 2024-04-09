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

        hash.initButtons();

        /* Switch tabs if necessary. */
        if (hash.tab) {
          this.switchTab(hash.tab);
        }

        /* Prepare worker message handler. */
        this.worker.onmessage = async (event) => {
          /* Check for reload recommendation. */
          if ("reload" in event.data && event.data["reload"]) {
            console.log("Worker thread recommended page reload.");
            window.location.reload();
          }

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

    let splash = document.getElementById("runtimepy-splash");

    let prevTime = 0;

    /* Main loop. */
    function render(time) {
      let deltaT = time - prevTime;

      /* Fade splash screen out if necessary. */
      if (splash) {
        let curr = window.getComputedStyle(splash).getPropertyValue("opacity");
        if (curr > 0) {
          splash.style.opacity = curr - (deltaT / 2500);
        } else {
          splash.style.display = "none";
          splash = undefined;
        }
      }

      /* Poll the currently shown tab. */
      if (shown_tab in tabs) {
        tabs[shown_tab].poll(time);
      }

      prevTime = time;
      requestAnimationFrame(render);
    }
    requestAnimationFrame(render);
  }
}
