tab.container.querySelector("button").onclick = async event => {
  /**/
  tab.send_message({kind : "button.pressed"});
  /**/
};

tab.message_handlers.push((data) => {
  console.log("-----" + tab.name + "-----");
  console.log(data);
  console.log("---------------------------");
});
