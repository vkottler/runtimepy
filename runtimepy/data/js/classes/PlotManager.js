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
}
