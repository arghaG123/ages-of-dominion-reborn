import test from 'node:test';
import assert from 'node:assert/strict';

class FakeContext {
  constructor() { this.state = 'running'; this.currentTime = 0; this.destination = {}; }
  createGain() { return { gain: { value: 1, setValueAtTime() {}, exponentialRampToValueAtTime() {} }, connect() {} }; }
  createOscillator() { return { type: '', frequency: { value: 0 }, connect() {}, start() {}, stop() {} }; }
  suspend() { this.state = 'suspended'; return Promise.resolve(); }
  resume() { this.state = 'running'; return Promise.resolve(); }
}
globalThis.AudioContext = FakeContext;

const { arm, applySettings, blip, suspendAudio, resumeAudio, audioCounts, nextSuspended } = await import('../src/client/audio.js');

test('background stops the motif timer and resume keeps one timer', async () => {
  arm({ music: 1, sfx: 1 });
  assert.equal(audioCounts().timer, true);
  const started = audioCounts().musicStarts;
  await new Promise(resolve => setTimeout(resolve, 450));
  assert.ok(audioCounts().musicStarts > started);
  const frozen = audioCounts().musicStarts;
  await suspendAudio();
  assert.equal(audioCounts().timer, false);
  assert.equal(audioCounts().state, 'suspended');
  await new Promise(resolve => setTimeout(resolve, 450));
  assert.equal(audioCounts().musicStarts, frozen);
  blip();
  assert.equal(audioCounts().sfxStarts, 0);
  await resumeAudio();
  assert.equal(audioCounts().timer, true);
  assert.equal(audioCounts().state, 'running');
  const after = audioCounts().musicStarts;
  await new Promise(resolve => setTimeout(resolve, 450));
  assert.ok(audioCounts().musicStarts > after);
  assert.equal(audioCounts().timer, true);
});

test('music and sound gains are independent, and focus does not resume a hidden page', async () => {
  applySettings({ music: 0, sfx: 1 });
  assert.equal(audioCounts().timer, false);
  const music = audioCounts().musicStarts;
  const sound = audioCounts().sfxStarts;
  await new Promise(resolve => setTimeout(resolve, 450));
  blip();
  assert.equal(audioCounts().musicStarts, music);
  assert.equal(audioCounts().sfxStarts, sound + 1);
  applySettings({ music: 0, sfx: 0 });
  blip();
  assert.equal(audioCounts().sfxStarts, sound + 1);
  let suspended = false;
  suspended = nextSuspended(suspended, 'visibility', true);
  assert.equal(suspended, true);
  suspended = nextSuspended(suspended, 'focus', true);
  assert.equal(suspended, true);
  suspended = nextSuspended(suspended, 'visibility', false);
  assert.equal(suspended, false);
  suspended = nextSuspended(suspended, 'blur', false);
  assert.equal(suspended, true);
  suspended = nextSuspended(suspended, 'focus', false);
  assert.equal(suspended, false);
});
