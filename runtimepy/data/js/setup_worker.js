/*
 * Do some heinous sh*t to create a worker from our 'text/js-worker' element.
 */
const worker = new Worker(window.URL.createObjectURL(new Blob(
    Array.prototype.map.call(
        document.querySelectorAll("script[type='text\/js-worker']"),
        (script) => script.textContent,
        ),
    {type : "text/javascript"},
    )));
