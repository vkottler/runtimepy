class WindowHashManager {
  constructor(loc) {
    this.loc = loc;
    this.original = this.hash();

    this.tab = "";
    if (this.original) {
      /*
       * determine current tab
       * determine state of tab + channel views
       */
    }
  }

  hash() {
    let result = undefined;
    if (this.loc.hash) {
      result = this.loc.hash.slice(1);
    }
    return result;
  }

  update() {
    // eventually needs to handle tab + channel view states
    window.location.hash = this.tab;
  }

  setTab(name) {
    this.tab = name;
    this.update();
  }
}

let hash = new WindowHashManager(window.location);
