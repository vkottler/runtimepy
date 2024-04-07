class WindowHashManager {
  constructor(loc) {
    this.loc = loc;
    this.original = this.hash();

    this.tab = "";
    this.tabsShown = true;
    this.channelsShown = true;
    this.plotChannels = {};
  }

  tabClick(event) {
    this.tabsShown = !this.tabsShown;
    this.update();
  }

  channelClick(event) {
    this.channelsShown = !this.channelsShown;

    /* Hide the divider when the channel table isn't shown. */
    let dividerDisplay = "block";
    if (!this.channelsShown) {
      dividerDisplay = "none";
    }
    for (let elem of document.querySelectorAll(".vertical-divider")) {
      elem.style.display = dividerDisplay;
    }

    this.update();
  }

  handlePlotChannelToggle(tabName, channel, state) {
    if (!(tabName in this.plotChannels)) {
      this.plotChannels[tabName] = {};
    }
    let channelStates = this.plotChannels[tabName];
    channelStates[channel] = state;

    this.update();
  }

  togglePlotChannel(tabName, channelName) {
    let elem = tabs[tabName].query("#plot-" + CSS.escape(channelName));
    if (elem) {
      elem.click();
    }
  }

  clearPlotChannels(tabName) {
    if (tabName in this.plotChannels) {
      let channels = this.plotChannels[tabName];
      for (let name in channels) {
        if (channels[name]) {
          this.togglePlotChannel(tabName, name);
        }
      }
    }
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
      let boolsChannels = this.original.split("/");
      let split = boolsChannels[0].split(".");
      this.tab = split[0];

      /* Toggle plot-channel check boxes. */
      for (let i = 1; i < boolsChannels.length; i++) {
        let nameChannels = boolsChannels[i].split(":");
        for (let chan of nameChannels[1].split(",")) {
          this.togglePlotChannel(nameChannels[0], chan);
        }
      }

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

    for (let tab in this.plotChannels) {
      let firstChan = true;
      let channels = this.plotChannels[tab];
      for (let name in channels) {
        if (channels[name]) {
          if (firstChan) {
            hash += "/" + tab + ":"
            firstChan = false;
          }

          if (hash.slice(-1) != ":") {
            hash += ",";
          }
          hash += name;
        }
      }
    }

    window.location.hash = hash;
  }

  setTab(name) {
    this.tab = name;
    this.update();
  }
}

let hash = new WindowHashManager(window.location);
