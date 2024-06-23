class OverlayManager {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = this.canvas.getContext("2d");
  }

  update(time) {
    let canvas = this.canvas;
    let ctx = this.ctx;

    /* Clear before drawing. */
    ctx.clearRect(0, 0, canvas.width, canvas.height);

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

  updateSize(width, height) {
    this.canvas.width = width;
    this.canvas.height = height;
  }
}
