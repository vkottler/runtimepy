for (let i = 0; i < 20; i++) {
  let msg = String(i);
  for (let j = 0; j < 10; j++) {
    msg = "Hello, world! " + msg;
  }
  tab.log(msg);
}

/*
tab.container.querySelector("button").onclick = async event => {
  //
  tab.send_message({kind : "button.pressed"});
  //
};

tab.message_handlers.push((data) => {
  console.log("-----" + tab.name + "-----");
  console.log(data);
  console.log("---------------------------");
});
 */
