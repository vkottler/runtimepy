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

    /* Individual message handlers. */
    this.message_handlers = {};
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

    for (const key in data) {
      if (key in this.message_handlers) {
        this.message_handlers[key](data[key]);
      } else if (!(key in response)) {
        console.log(`(not handled) ${key}:`);
        console.log(data[key]);
      }
    }

    /* Send our response. */
    for (const _ in response) {
      this.send_json(response);
      return;
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

    /*
     * Nothing to do from here. Recommend page refresh (to UI thread) for now.
     */
    postMessage({reload : true});
  }

  onerror(event) {
    console.log(`Connection ${this.toString()} error.`);
    console.log(event);
  }
}
