class PlotModalManager {
  constructor(element) {
    this.container = element;

    this.header = this.container.querySelector(".modal-header");
    this.body = this.container.querySelector(".modal-body");
    this.footer = this.container.querySelector(".modal-footer");

    this.byEnv = {};
  }

  handleChannelToggle(env, channel, state) {
    if (!(env in this.byEnv)) {
      this.byEnv[env] = {};
    }
    let byEnv = this.byEnv[env];

    /* Update state.*/
    byEnv[channel] = state;

    /* Update UI. */
    this.updateInner();
  }

  updateInner() {
    let content = "";

    for (let name in this.byEnv) {
      let env = this.byEnv[name];
      for (let chan in env) {
        if (env[chan]) {
          content += `${name}:${chan}<br>`;
        }
      }
    }

    this.body.innerHTML = content;
  }
}

let modalManager = null;
