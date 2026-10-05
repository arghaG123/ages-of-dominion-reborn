let ctx, music, sfx, musicTimer, appSuspended = false;
let musicStarts = 0, sfxStarts = 0;
export const MUSIC_MOTIF = [196, 247, 294, 247, 220, 247, 330, 294];
export const BLIP_HZ = 523;
export function audioCounts() { return { musicStarts, sfxStarts, timer: Boolean(musicTimer), suspended: appSuspended, state: ctx?.state ?? 'closed' }; }
export function nextSuspended(suspended, event, hidden) {
  if (event === 'blur' || event === 'pagehide') return true;
  if (event === 'visibility') return Boolean(hidden);
  if (event === 'focus') return hidden ? suspended : false;
  return suspended;
}
function startMusic() {
  if (musicTimer || !ctx || ctx.state !== 'running' || appSuspended || !music || music.gain.value <= 0) return;
  let step = 0;
  const pulse = () => {
    if (appSuspended || !ctx || ctx.state !== 'running' || !music || music.gain.value <= 0) return;
    musicStarts += 1;
    const osc = ctx.createOscillator();
    const env = ctx.createGain();
    osc.type = 'triangle';
    osc.frequency.value = MUSIC_MOTIF[step % MUSIC_MOTIF.length];
    env.gain.setValueAtTime(0.0001, ctx.currentTime);
    env.gain.exponentialRampToValueAtTime(0.08, ctx.currentTime + 0.02);
    env.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.35);
    osc.connect(env);
    env.connect(music);
    osc.start();
    osc.stop(ctx.currentTime + 0.4);
    step += 1;
  };
  pulse();
  musicTimer = setInterval(pulse, 420);
}
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
  if (!appSuspended && settings.music > 0 && ctx.state === 'running') startMusic();
  return ctx.state;
}
export function applySettings(settings) {
  if (!music || !settings) return;
  music.gain.value = settings.music;
  sfx.gain.value = settings.sfx;
  if (settings.music <= 0 && musicTimer) { clearInterval(musicTimer); musicTimer = null; }
  if (!appSuspended && settings.music > 0 && ctx?.state === 'running') startMusic();
}
export function suspendAudio() {
  appSuspended = true;
  if (musicTimer) { clearInterval(musicTimer); musicTimer = null; }
  if (ctx && ctx.state === 'running' && typeof ctx.suspend === 'function') return Promise.resolve(ctx.suspend());
  return Promise.resolve();
}
export function resumeAudio() {
  appSuspended = false;
  const pending = ctx && ctx.state === 'suspended' && typeof ctx.resume === 'function' ? Promise.resolve(ctx.resume()) : Promise.resolve();
  return pending.then(() => { if (!appSuspended && music && music.gain.value > 0) startMusic(); });
}
export function blip() {
  if (!ctx || ctx.state !== 'running' || appSuspended || !sfx || sfx.gain.value <= 0) return;
  sfxStarts += 1;
  const tone = ctx.createOscillator();
  tone.frequency.value = BLIP_HZ;
  tone.connect(sfx);
  tone.start();
  tone.stop(ctx.currentTime + 0.06);
}
