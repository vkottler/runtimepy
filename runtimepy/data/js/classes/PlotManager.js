class PlotManager {
  constructor() {
    /* null */
    this.plots = {};
    this.contextType = "2d";
    this.contexts = {};
    this.shown = "UNKNOWN";
  }

  render(time) {
    if (this.shown in this.plots) {
      this.drawPlot(this.shown, time);
    }
  }

  async handleMessage(data) {
    let name = data["name"];

    /* Handle initial transfer. */
    if ("canvas" in data) {
      this.plots[name] = data["canvas"];
      this.contexts[name] = data["canvas"].getContext(this.contextType);
    }

    /* Handle size updates. */
    if ("width" in data && "height" in data) {
      this.plots[name].width = data["width"];
      this.plots[name].height = data["height"];
    }

    if ("shown" in data) {
      /* handle shown state */
      if (data["shown"]) {
        this.shown = name;
      }
    }
  }

  drawPlot(name, time) {
    const canvas = this.plots[name];
    const ctx = this.contexts[name];

    ctx.fillStyle = "purple";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "green";
    let size = 25;

    ctx.fillRect(size, size, size, size);
    ctx.fillRect(canvas.width - (2 * size), size, size, size);
    ctx.fillRect(size, canvas.height - (2 * size), size, size);
    ctx.fillRect(canvas.width - (2 * size), canvas.height - (2 * size), size,
                 size);

    ctx.fillStyle = "blue";
    ctx.font = "24px monospace";
    let y = canvas.height / 2;
    ctx.fillText(Date.now(), canvas.width / 2, y);
    ctx.fillText(time, canvas.width / 2, y + 24);
  }
}
