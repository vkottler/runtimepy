class JsonConnection {
  constructor(websocket_url) {
    this.conn = new WebSocket(websocket_url);
    this.conn.binaryType = "arraybuffer";

    /* Register handlers. */
    this.conn.onmessage = this.onmessage.bind(this);
    // register handlers for connection state + need to mess with that

    /* Runtime resources. */
    this.decoder = new TextDecoder();
  }

  /*
   * This is where we need a different implementation for the data stream
   * connection.
   */
  handle_payload(buffer) {
    this.handle_json(JSON.parse(this.decoder.decode(buffer)));
  }

  handle_json(data) {
    // next up!!!
    console.log(data);
  }

  /* Need a method to send a JSON object. */

  onmessage(event) {
    let buffer = event.data;

    while (buffer.byteLength > 0) {
      /* Read header, advance buffer. */
      let length = new DataView(buffer).getUint32();
      buffer = buffer.slice(4);

      /* Read message, advance buffer.*/
      this.handle_payload(buffer.slice(0, length));
      buffer = buffer.slice(length);
    }
  }
}
