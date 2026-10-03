// Persisted campaign randomness. The reference pick/rnd helpers call Math.random
// and cannot be reloaded, so this fresh generator is a 32-bit LCG stored in the save.
// Rendering and previews must not call it.

export function nextUnit(state) {
  const rngState = (Math.imul(state.rngState >>> 0, 1664525) + 1013904223) >>> 0;
  return { rngState, unit: rngState / 4294967296 };
}

export function draw(state) {
  const rolled = nextUnit(state);
  state.rngState = rolled.rngState;
  return rolled.unit;
}

export function drawInt(state, count) {
  if (!Number.isInteger(count) || count < 1) throw new Error('Invalid random range');
  return Math.floor(draw(state) * count);
}
