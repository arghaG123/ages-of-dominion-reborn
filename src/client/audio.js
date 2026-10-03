let ctx, music, sfx;
export function arm(settings) {
  if (!ctx) {
    ctx = new AudioContext();
    music = ctx.createGain();
    sfx = ctx.createGain();
    music.connect(ctx.destination);
    sfx.connect(ctx.destination);
  }
  music.gain.value = settings.music;
  sfx.gain.value = settings.sfx;
  return ctx.state;
}
export function applySettings(settings) {
  if (!music || !settings) return;
  music.gain.value = settings.music;
  sfx.gain.value = settings.sfx;
}
export function blip() {
  if (!ctx || ctx.state !== 'running') return;
  const tone = ctx.createOscillator();
  tone.frequency.value = 523;
  tone.connect(sfx);
  tone.start();
  tone.stop(ctx.currentTime + 0.06);
}
