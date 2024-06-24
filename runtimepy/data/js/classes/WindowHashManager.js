class WindowHashManager {
  constructor(loc) {
    this.loc = loc;
    this.original = this.hash();

    this.tab = "";
    this.tabFilter = "";
    this.tabsShown = true;
    this.channelsShown = true;
    this.plotChannels = {};
    this.filters = {};
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

  handleChannelFilter(tabName, value) {
    this.filters[tabName] = value;
    this.update();
  }

  handlePlotChannelToggle(tabName, channel, state) {
    /* Service settings modal. */
    if (modalManager) {
      modalManager.handleChannelToggle(tabName, channel, state);
    }

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

  setTabFilter(value) {
    this.tabFilter = value;
    this.update();
  }

  updateTabFilter(value) {
    this.tabFilter = value;
    if (tabFilter) {
      tabFilter.input.value = value;
      tabFilter.updateStyles(value);
    }
  }

  setTabChannelFilter(tabName, value) {
    this.filters[tabName] = value;

    let elem = tabs[tabName].query("#channel-filter");
    if (elem) {
      elem.value = value;
      tabs[tabName].updateChannelStyles(value);
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

    /* Click handlers for new window buttons. */
    for (const button of document.querySelectorAll(".window-button")) {
      button.onclick = () => {
        /* Save some state. */
        let currTab = this.tab;

        /* Update state to prepare for hash-string building. */
        this.tab = button.id;
        this.tabsShown = false;

        let hash = this.buildHash();

        /* Restore some state. */
        this.tab = currTab;
        this.tabsShown = true;

        window.open(this.loc.origin + this.loc.pathname + "#" + hash, "_blank",
                    "height=400,width=800,popup");
      }
    };

    /* Parse status (powers refreshes and link sharing). */
    if (this.original) {
      let boolsChannels = this.original.split("/");
      let split = boolsChannels[0].split(",");
      this.tab = split[0];

      /* Toggle plot-channel check boxes. */
      for (let i = 1; i < boolsChannels.length; i++) {
        let nameChannels = boolsChannels[i].split(":");
        for (let chan of nameChannels[1].split(",")) {
          if (!chan.includes("=")) {
            /* Handle regular channel names. */
            this.togglePlotChannel(nameChannels[0], chan);
          } else {
            /* Handle key-value pairs. */
            let keyVal = chan.split("=");
            if (keyVal.length == 2 && keyVal[0] == "filter" && keyVal[1]) {
              this.setTabChannelFilter(nameChannels[0], keyVal[1]);
            }
          }
        }
      }

      if (split.includes("hide-tabs")) {
        tabButton.click();
      }
      if (split.includes("hide-channels")) {
        channelsButton.click();
      }

      /* Check for tab filter. */
      for (let item of split) {
        if (item.includes("=")) {
          let keyVal = item.split("=");
          if (keyVal.length == 2 && keyVal[0] == "filter" && keyVal[1]) {
            this.updateTabFilter(keyVal[1]);
          }
        }
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

  buildHash() {
    let hash = this.tab;

    if (this.tabFilter) {
      hash += ",filter=" + this.tabFilter;
    }
    if (!this.tabsShown) {
      hash += ",hide-tabs"
    }
    if (!this.channelsShown) {
      hash += ",hide-channels"
    }

    for (let tab in tabs) {
      let firstChan = true;

      /* Write plot channels if present. */
      if (tab in this.plotChannels) {
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

      /* Write tab filter if present. */
      if (tab in this.filters && this.filters[tab]) {
        if (firstChan) {
          hash += "/" + tab + ":"
          firstChan = false;
        }

        if (hash.slice(-1) != ":") {
          hash += ",";
        }
        hash += "filter=" + this.filters[tab];
      }
    }

    return hash;
  }

  update() { window.location.hash = this.buildHash(); }

  setTab(name) {
    this.tab = name;
    this.update();
  }
}

let hash = new WindowHashManager(window.location);
