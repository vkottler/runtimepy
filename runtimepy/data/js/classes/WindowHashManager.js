class WindowHashManager {
  constructor(loc) {
    this.loc = loc;
    this.original = this.hash();

    this.tab = "";
    this.tabsShown = true;
    this.channelsShown = true;
  }

  tabClick(event) {
    this.tabsShown = !this.tabsShown;
    this.update();
  }

  channelClick(event) {
    this.channelsShown = !this.channelsShown;
    this.update();
  }

  initButtons() {
    /* Click handler for tabs hide/show. */
    let tabButton = document.getElementById("tabs-button");
    if (tabButton) {
      tabButton.addEventListener("click", this.tabClick.bind(this));
    }

    /* Click handler for channels hide/show. */
    let channelsButton = document.getElementById("channels-button");
    if (channelsButton) {
      channelsButton.addEventListener("click", this.channelClick.bind(this));
    }

    /* Parse status (powers refreshes and link sharing). */
    if (this.original) {
      let split = this.original.split(".");
      this.tab = split[0];

      if (split.includes("hide-tabs")) {
        tabButton.click();
      }
      if (split.includes("hide-channels")) {
        channelsButton.click();
      }
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
    let hash = this.tab

    if (!this.tabsShown) {
      hash += ".hide-tabs"
    }
    if (!this.channelsShown) {
      hash += ".hide-channels"
    }

    window.location.hash = hash;
  }

  setTab(name) {
    this.tab = name;
    this.update();
  }
}

let hash = new WindowHashManager(window.location);
