// Presentation clock. Simulation time advances only while the page is active.
// Reduced motion and background freeze the render sample. This is not a device frame-rate claim.

export function createFrameClock({ paused, onFrame, requestFrame = globalThis.requestAnimationFrame, cancelFrame = globalThis.cancelAnimationFrame, now = () => globalThis.performance.now() } = {}) {
  let handle = 0;
  let last = 0;
  let sim = 0;
  const sample = { sim: 0, render: 0, dt: 0, paused: true };
  function frame(stamp) {
    const t = stamp ?? now();
    const dt = last ? Math.min(0.05, Math.max(0, (t - last) / 1000)) : 0;
    last = t;
    const hold = Boolean(paused?.());
    if (!hold) sim += dt;
    sample.sim = sim;
    sample.render = sim;
    sample.dt = hold ? 0 : dt;
    sample.paused = hold;
    onFrame?.(sample);
    handle = requestFrame(frame);
  }
  return {
    start() {
      if (handle) return;
      last = 0;
      handle = requestFrame(frame);
    },
    stop() {
      if (handle && cancelFrame) cancelFrame(handle);
      handle = 0;
    },
    sample() { return { ...sample }; },
  };
}

export function travelSample(points, u) {
  if (!Array.isArray(points) || points.length === 0) throw new Error('Empty travel');
  const start = points[0];
  if (points.length === 1 || u <= 0) return { x: start[0] + 0.5, y: start[1] + 0.5, facing: 1, moving: false, index: 0 };
  const clamped = Math.min(0.999999, u);
  const span = points.length - 1;
  const scaled = clamped * span;
  const index = Math.min(span - 1, Math.floor(scaled));
  const f = scaled - index;
  const a = points[index];
  const b = points[index + 1];
  const dx = b[0] - a[0];
  return {
    x: a[0] + 0.5 + dx * f,
    y: a[1] + 0.5 + (b[1] - a[1]) * f,
    facing: dx < 0 ? -1 : 1,
    moving: f > 0 && f < 1 || u < 1,
    index,
  };
}

export function travelProgress(started, now, duration) {
  if (!(duration > 0)) return 1;
  return Math.max(0, Math.min(1, (now - started) / duration));
}
