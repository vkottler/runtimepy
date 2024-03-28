const tau = 2 * Math.PI;

class RuntimepyAudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();

    this.sampleRate = null;
    this.time = 0.0;

    this.port.onmessage = (e) => {
      if ("sampleRate" in e.data) {
        this.sampleRate = e.data["sampleRate"];
        this.samplePeriod = 1.0 / this.sampleRate;
      }
    };
  }

  nextSample() {
    /* Sine wave example. */
    let val = Math.sin(tau * this.time * 440);

    this.time += this.samplePeriod;

    return val;
  }

  process(inputList, outputList, parameters) {
    /* Can't do anything until we know the sample rate. */
    if (!this.sampleRate) {
      return;
    }

    /* Ignore all inputs values. */

    let i = 0;
    while (i < outputList[0][0].length) {
      /* Get next value. */
      let val = this.nextSample();

      /* Handle outputs. */
      for (let output of outputList) {
        for (let channel of output) {
          channel[i] = val;
        }
      }

      i++;
    }

    return true;
  }
}

registerProcessor("runtimepy-audio-processor", RuntimepyAudioProcessor);
