/* Resources. */
const decoder = new TextDecoder();
const encoder = new TextEncoder();

const forward_keys = [ "__id__", "loopback" ];

class JsonConnection {
  constructor(name, websocket_url) {
    this.name = name;
    this.conn = new WebSocket(websocket_url);
    this.conn.binaryType = "arraybuffer";

    /* State. */
    this.connected = new Promise((resolve, reject) => {
      this.resolve = resolve;
      this.reject = reject
    });

    /* Register handlers. */
    this.conn.onclose = this.onclose.bind(this);
    this.conn.onerror = this.onerror.bind(this);
    this.conn.onmessage = this.onmessage.bind(this);
    this.conn.onopen = this.onopen.bind(this);
  }

  /*
   * This is where we need a different implementation for the data stream
   * connection.
   */
  handle_payload(buffer) {
    this.handle_json(JSON.parse(decoder.decode(buffer)));
  }

  handle_json(data) {
    let response = {};

    /* Forward some keys directly. */
    for (let idx in forward_keys) {
      let key = forward_keys[idx];
      if (key in data) {
        response[key] = data[key];
      }
    }

    // handle any keys we haven't handled yet
    console.log(data);

    /* Send our response. */
    if (response) {
      this.send_json(response);
    }
  }

  /* Need a method to send a JSON object. */
  send_json(data) {
    /* Convert object to bytes. */
    let message = encoder.encode(JSON.stringify(data));

    /* Create buffer for sending and set size. */
    let buffer = new ArrayBuffer(message.byteLength + 4);
    new DataView(buffer).setUint32(0, message.byteLength);

    /* Write message into buffer. */
    new Uint8Array(buffer).subarray(4).set(message);

    /* Send. */
    this.conn.send(buffer);
  }

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

  toString() { return `'${this.name}' (${this.conn.url})`; }

  onopen(event) {
    console.log(`Connection ${this.toString()} open.`);
    this.resolve();
  }

  onclose(event) {
    console.log(`Connection ${this.toString()} closed.`);
    this.reject();
  }

  onerror(event) {
    console.log(`Connection ${this.toString()} error.`);
    console.log(event);
  }
}
