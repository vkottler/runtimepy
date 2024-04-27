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

    this.webglps = {};
    this.lines = {};
  }

  render(time) {
    if (this.shown in this.plots) {
      this.drawPlot(this.shown, time);
    }
  }

  updateSize(name) {
    let canvas = this.plots[name];

    if (name in this.webglps) {
      const wglp = this.webglps[name];

      /* is this the demo? */
      const color = new WebglPlotBundle.ColorRGBA(Math.random(), Math.random(),
                                                  Math.random(), 1);

      const line = new WebglPlotBundle.WebglLine(color, canvas.width);
      line.arrangeX();
      wglp.removeAllLines();
      wglp.addLine(line);
      this.lines[name] = line;

      wglp.viewport(0, 0, canvas.width, canvas.height);
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

    /* Handle shown state. */
    if ("shown" in data) {
      if (data["shown"]) {
        this.shown = name;

        /* Create webgl context for this tab. */
        let created = name in this.webglps || name in this.contexts;
        if (!created) {
          if (webglContextCount < webglContextMax && name in this.plots) {
            const canvas = this.plots[name];

            const glps = new WebglPlotBundle.WebglPlot(canvas);
            this.webglps[name] = glps;

            webglContextCount++;
            this.updateSize(name);
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
    const canvas = this.plots[name];

    if (name in this.webglps) {
      const wglp = this.webglps[name];

      const freq = 0.001;
      const amp = 0.5;
      const noise = 0.1;

      let line = this.lines[name];
      for (let i = 0; i < line.numPoints; i++) {
        const ySin = Math.sin(Math.PI * i * freq * Math.PI * 2);
        const yNoise = Math.random() - 0.5;
        line.setY(i, ySin * amp + yNoise * noise);
      }

      wglp.update();

    } else if (name in this.contexts) {
      this.draw2d(canvas, this.contexts[name], time);
    }
  }
}
