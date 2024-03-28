tab.message_handlers.push((data) => {
  console.log("-----" + tab.name + "-----");
  console.log(data);
  console.log("---------------------------");
});

let audioContext = null;
let processorNode = null;

async function audioProcessor() {
  if (!audioContext) {
    audioContext = new AudioContext();
  }

  if (!processorNode) {
    await audioContext.audioWorklet.addModule("js/audio.js");
    processorNode =
        new AudioWorkletNode(audioContext, "runtimepy-audio-processor");
    await audioContext.suspend();
  }

  return processorNode;
}

let newProcessorNode = null;
let source = null;
let running = false;

tab.query("#test-button").onclick = async event => {
  tab.worker.send({kind : "button.pressed"});

  if (!newProcessorNode) {
    newProcessorNode = await audioProcessor();

    /* Send worklet information about the audio stream. */
    newProcessorNode.port.postMessage({sampleRate : audioContext.sampleRate});

    /* THIS IS WORKING */
    newProcessorNode.port.onmessage = (e) => { console.log(e.data); };
  }

  if (!source) {
    source = new ConstantSourceNode(audioContext, {offset : 0.1});
    source.connect(newProcessorNode).connect(audioContext.destination);
    source.start();
  }

  console.log(audioContext.destination);

  if (audioContext.state != "running") {
    await audioContext.resume();
  } else {
    await audioContext.suspend();
  }
};
