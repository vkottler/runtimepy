class TabFilter {
  constructor(container) {
    this.container = container;

    /* Find input element. */
    this.input = this.container.querySelector("input");
    this.input.addEventListener("keydown", this.keydown.bind(this));

    /* Create a mapping of tab name to tab element. */
    this.buttons = {};
    for (let button of this.container.querySelectorAll("button")) {
      let name = button.id.split("-")[1];
      this.buttons[name] = button;
    }
  }

  updateStyles(pattern) {
    hash.setTabFilter(pattern);

    if (!pattern) {
      pattern = ".*";
    }
    const re = new RegExp(pattern);

    for (let [name, elem] of Object.entries(this.buttons)) {
      if (re.test(name)) {
        elem.style.display = "block";
      } else if (!elem.classList.contains("active")) {
        elem.style.display = "none";
      }
    }
  }

  keydown(event) {
    if (event.key == "Enter") {
      this.input.value = "";
      this.updateStyles(this.input.value);
    } else {
      let curr = this.input.value;
      if (event.key == "Backspace") {
        curr = curr.slice(0, -1);
      } else {
        curr += event.key;
      }
      this.updateStyles(curr);
    }
  }
}
