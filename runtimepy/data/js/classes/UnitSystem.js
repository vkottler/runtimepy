class UnitSystem {
  constructor(prefixes, divisor) {
    this.prefixes = prefixes;
    this.divisor = divisor;
  }

  traverse(value, max_prefix = 3, iteration = 0) {
    let decimal = value;
    let fractional = 0;

    let maxIteration = Math.min(this.prefixes.length - 1, max_prefix);
    while (decimal >= this.divisor && iteration < maxIteration) {
      fractional = decimal % this.divisor;
      decimal = Math.floor(decimal / this.divisor);
      iteration += 1;
    }

    return [ decimal, fractional, this.prefixes[iteration] ];
  }
}

const siUnits =
    new UnitSystem([ "n", "u", "m", " ", "k", "M", "G", "T" ], 1000);
const kibiUnits = new UnitSystem(
    [ "", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi" ], 1024);

function nanosString(deltaNs) {
  let traversed = siUnits.traverse(deltaNs);

  return [
    String((traversed[0] + traversed[1] / 1000).toFixed(3)), traversed[2]
  ];
}
