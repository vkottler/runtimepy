class TabFilter {
  constructor(container) {
    this.container = container;

    /* Find input element. */
    this.input = this.container.querySelector("input");
    this.input.onkeypress = this.onkeypress.bind(this);
  }

  onkeypress(event) {
    if (event.key == "Enter") {
      this.input.value = "";
    } else {
      let curr = this.input.value + event.key;
      console.log(curr);

      /* Iterate over siblings, hide/show. */
    }
  }
}
