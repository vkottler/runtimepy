import("https://cdn.jsdelivr.net/gh/danchitnis/" +
       "webgl-plot@master/dist/webglplot.umd.min.js");

let webglContextCount = 0;

/* Warnings start at this amount. */
const webglContextMax = 4;

class PlotManager {
  constructor() {
    this.plots = {};

    this.contextType = "2d";
    this.contexts = {};

    this.shown = "UNKNOWN";

    this.drawers = {};
    this.channelsToPlot = {};
  }

  handlePlotChannelState(name, channel, state) {
    if (name in this.drawers) {
      this.drawers[name].channelState(channel, state);
    } else if (state) {
      if (!(name in this.channelsToPlot)) {
        this.channelsToPlot[name] = [];
      }
      this.channelsToPlot[name].push(channel);
    }
  }

  handlePoints(name, points) {
    if (name in this.drawers) {
      this.drawers[name].handlePoints(points);
    }
  }

  render(time) {
    if (this.shown in this.plots) {
      this.drawPlot(this.shown, time);
    }
  }

  updateSize(name) {
    if (name in this.drawers) {
      this.drawers[name].updateSize();
    }
  }

  async handleMessage(data) {
    let name = data["name"];

    /* Handle initial transfer. */
    if ("canvas" in data) {
      this.plots[name] = data["canvas"];
    }

    /* Handle size updates. */
    if ("width" in data && "height" in data) {
      let canvas = this.plots[name];
      canvas.width = data["width"];
      canvas.height = data["height"];
      this.updateSize(name);
    }

    /* Handle channel state changes. */
    if ("channel" in data && "state" in data) {
      this.handlePlotChannelState(data["name"], data["channel"], data["state"]);
    }

    /* Handle shown state. */
    if ("shown" in data) {
      if (data["shown"]) {
        this.shown = name;

        /* Create webgl context for this tab. */
        let created = name in this.drawers || name in this.contexts;
        if (!created) {
          if (webglContextCount < webglContextMax && name in this.plots) {
            let drawer = new PlotDrawer(this.plots[name]);
            this.drawers[name] = drawer;

            webglContextCount++;
            this.updateSize(name);

            /* Handle plotting channels immediately if necessary. */
            if (name in this.channelsToPlot) {
              for (let chan of this.channelsToPlot[name]) {
                drawer.channelState(chan, true);
              }
              delete this.channelsToPlot[name];
            }

            created = true;
          }
        }

        /* Create backup 2D context if necessary. */
        if (!created && !(name in this.contexts)) {
          if (name in this.plots) {
            this.contexts[name] = this.plots[name].getContext(this.contextType);
          }
        }
      }
    }
  }

  draw2d(canvas, ctx, time) {
    /* Background (match bootstrap). */
    ctx.fillStyle = "#212529";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "#495057";
    let size = 25;

    ctx.fillRect(size, size, size, size);
    ctx.fillRect(canvas.width - (2 * size), size, size, size);
    ctx.fillRect(size, canvas.height - (2 * size), size, size);
    ctx.fillRect(canvas.width - (2 * size), canvas.height - (2 * size), size,
                 size);

    ctx.fillStyle = "#cce2e6";
    ctx.font = "24px monospace";
    let y = (canvas.height / 3) + 24;
    let x = (canvas.width / 3);
    ctx.fillText("Future plot area!", x, y);
    ctx.fillText(Date.now(), x, y + 48);
    ctx.fillText(time, x, y + 72);
  }

  drawPlot(name, time) {
    if (name in this.drawers) {
      this.drawers[name].update();
    } else if (name in this.contexts) {
      this.draw2d(this.plots[name], this.contexts[name], time);
    }
  }
}
