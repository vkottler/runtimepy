tab.query("#test-button").onclick = async event => {
  //
  tab.worker.send({kind : "button.pressed"});
  //
};

tab.message_handlers.push((data) => {
  console.log("-----" + tab.name + "-----");
  console.log(data);
  console.log("---------------------------");
});
