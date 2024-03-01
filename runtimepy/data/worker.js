/* JSON connection message parsing. */
function json_conn_entry(conn) {
  conn.binaryType = "arraybuffer";

  /* Handle messages. */
  conn.onmessage = (event) => {
    let buffer = event.data;
    let decoder = new TextDecoder();

    while (buffer.byteLength > 0) {
      /* Read header, advance buffer. */
      let length = new DataView(buffer).getUint32();
      buffer = buffer.slice(4);

      /* Read message, advance buffer.*/
      handle_json_message(conn,
                          JSON.parse(decoder.decode(buffer.slice(0, length))));
      buffer = buffer.slice(length);
    }
  }
}

/* Worker entry. */
function start(config) {
  json_conn_entry(new WebSocket(config["websocket_url"]));
}

started = false;

/* Handle messages from the main thread. */
onmessage = (event) => {
  /* First message.*/
  if (!started) {
    start(event.data);
    started = true;
  } else {
    /* Additional messages not handled. */
    console.log(event.data);
  }
};
