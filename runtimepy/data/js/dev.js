document.getElementById(name + "-button").onclick = async event => {
  /**/
  tab.send_message({kind : "button.pressed"});
  /**/
};
