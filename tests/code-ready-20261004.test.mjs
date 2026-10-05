import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import crypto from 'node:crypto';
import { occupiedPortMessage, selectedPort } from '../scripts/dev-port.mjs';
import reviewMount from '../src/data/mount-review-v1.json' with { type: 'json' };
import staticMounts from '../src/data/static-mounts-v1.json' with { type: 'json' };
import { staticMountForAge } from '../src/client/actor.js';
import { pendingPortrait, portraitCard } from '../src/client/portraits.js';
import plates from '../src/data/plate-catalog.json' with { type: 'json' };
import binding from '../src/data/anatomy-binding-v1.json' with { type: 'json' };
import { paintedPose } from '../src/client/anatomy.js';
import { ACTIVE_AFFINE } from '../src/client/presentation.js';
import scene from '../src/data/stone-scene.json' with { type: 'json' };

test('the preview port is selected without stopping another listener', () => {
  assert.equal(selectedPort([], {}), 4173);
  assert.equal(selectedPort(['--port', '4188'], { PORT: '4173' }), 4188);
  assert.equal(selectedPort(['--port=4200'], {}), 4200);
  assert.equal(selectedPort([], { PORT: '4300' }), 4300);
  assert.throws(() => selectedPort(['--port', 'nope'], {}), /Selected port/);
  assert.match(occupiedPortMessage(4173), /4173/);
  assert.match(occupiedPortMessage(4173), /No other process was stopped/);
});

test('an occupied selected port reports the port and leaves the listener running', async () => {
  const port = 47000 + Math.floor(Math.random() * 1000);
  const first = spawn(process.execPath, ['scripts/serve.mjs', '--port', String(port)], { stdio: ['ignore', 'pipe', 'pipe'] });
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('server did not start')), 4000);
    first.stdout.on('data', chunk => {
      if (String(chunk).includes(String(port))) {
        clearTimeout(timer);
        resolve();
      }
    });
    first.on('exit', code => reject(new Error('first server exited ' + code)));
  });
  const second = spawn(process.execPath, ['scripts/serve.mjs', '--port', String(port)], { stdio: ['ignore', 'pipe', 'pipe'] });
  const errorText = await new Promise(resolve => {
    let text = '';
    second.stderr.on('data', chunk => { text += chunk; });
    second.on('exit', () => resolve(text));
  });
  assert.match(errorText, new RegExp(`Selected port ${port}`));
  assert.match(errorText, /No other process was stopped/);
  assert.equal(first.exitCode, null);
  first.kill();
  await new Promise(resolve => first.on('exit', resolve));
});

test('npm dev reports a selected port instead of hopping to Vite', () => {
  const pack = JSON.parse(fs.readFileSync(new URL('../package.json', import.meta.url), 'utf8'));
  assert.equal(pack.scripts.dev, 'node scripts/serve.mjs');
  assert.equal(pack.scripts['build:apk'], 'node scripts/build-apk.mjs');
});

test('the v4 horse is a single-pose review and the floored v3 horse stays withheld', () => {
  const bytes = fs.readFileSync(new URL(`../${reviewMount.file}`, import.meta.url));
  assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), reviewMount.sha256);
  assert.equal(reviewMount.status, 'BOUNDED_REVIEW_SAMPLE_RESIDUAL_HAIRLINE');
  assert.equal(reviewMount.gait, 'single-pose');
  assert.equal(reviewMount.hoofArticulation, 'not-separated');
  assert.equal(binding.withheld.some(row => row.file === reviewMount.withheldWorldMount), true);
  assert.equal(reviewMount.file.includes('/v4/'), true);
});

test('the ancient knight crop stays pending and the medieval card stays gated', () => {
  assert.equal(portraitCard('knight', 0), null);
  assert.equal(portraitCard('knight', 3).era, 'medieval');
  const pending = pendingPortrait('knight', 0);
  assert.equal(pending.status, 'PENDING_CARD_REVIEW');
  assert.equal(pending.era, 'ancient');
  const hash = crypto.createHash('sha256').update(fs.readFileSync(pending.file)).digest('hex');
  assert.equal(hash, pending.sha256);
  assert.equal(pendingPortrait('knight', 3), null);
  assert.equal(pending.file.includes('mounted'), false);
});

test('reviewed substitution plates keep their measured hashes and roles', () => {
  for (const key of ['2-melee', '5-heavy']) {
    const plate = plates.troops[key];
    assert.equal(plate.pose, 'single');
    assert.equal(plate.file.startsWith('assets/derivatives/substitutions/v3/'), true);
    const hash = crypto.createHash('sha256').update(fs.readFileSync(plate.file)).digest('hex');
    assert.equal(hash, plate.sha256);
  }
  assert.match(plates.rejected['troop-industrial-heavy'], /rifleman/);
});

test('the ranger binding uses corrected roles and keeps the active kingdom contract', () => {
  assert.equal(binding.classId, 'ranger');
  assert.equal(binding.overlapPass, true);
  assert.equal(binding.parts.torso.role, 'torso');
  assert.equal(binding.parts.head.role, 'head');
  assert.equal(binding.parts.bow.role, 'bow');
  assert.equal(binding.parts.quiver.role, 'quiver');
  assert.equal(binding.parts.bootL.role, 'boot');
  assert.ok(binding.missing.includes('handLeft'));
  assert.equal(binding.mount.status, 'WITHHELD');
  const drawn = Object.values(binding.parts).map(part => part.file).join(' ');
  assert.equal(drawn.includes('forearm_hand'), false);
  assert.equal(drawn.includes('quiver_cloak'), false);
  for (const clip of ['idle', 'walk', 'work', 'attack', 'hit', 'death', 'mountWalk']) {
    const pose = paintedPose(clip, 0.35, false);
    assert.ok(Math.abs(pose.thighL) <= binding.testedAngles.thigh);
    assert.ok(Math.abs(pose.shinL) <= binding.testedAngles.shin);
    assert.ok(Math.abs(pose.bow) <= binding.testedAngles.bow);
  }
  assert.deepEqual(scene.camera, ACTIVE_AFFINE);
  assert.equal(scene.hall.matrix[0][0], 0.1312);
  assert.equal(scene.runtimeApproved, false);
});

test('kept v4 plates match their files and rejected slabs stay unbound', () => {
  const kept = {
    '2-heavy': 'assets/derivatives/actors/v4/troop-iron-heavy.png',
    '4-heavy': 'assets/derivatives/actors/v4/troop-gunpowder-heavy.png',
    '7-ranged': 'assets/derivatives/actors/v4/troop-future-ranged.png',
    '7-heavy': 'assets/derivatives/actors/v4/troop-future-heavy.png',
  };
  for (const [key, file] of Object.entries(kept)) {
    const plate = plates.troops[key];
    assert.equal(plate.file, file);
    assert.equal(plate.pose, 'single');
    assert.equal(plate.staticMaxHeight, 130);
    const hash = crypto.createHash('sha256').update(fs.readFileSync(plate.file)).digest('hex');
    assert.equal(hash, plate.sha256);
  }
  for (const key of ['0-melee', '0-ranged', '5-ranged']) {
    assert.equal(plates.troops[key].file.includes('/v4/'), false);
    assert.equal(typeof plates.troops[key].provisional, 'string');
  }
  assert.match(plates.rejected['knight-mounted-master'], /medieval/);
  assert.equal(plates.troops['2-melee'].file.includes('substitutions/v3'), true);
  assert.equal(plates.troops['5-heavy'].file.includes('substitutions/v3'), true);
  for (const mount of Object.values(staticMounts.mounts)) {
    assert.equal(mount.displayHeight, 64);
    assert.equal(mount.rider, 'withheld-seat-not-measured');
    const hash = crypto.createHash('sha256').update(fs.readFileSync(mount.file)).digest('hex');
    assert.equal(hash, mount.sha256);
  }
  assert.equal(staticMountForAge(5), null);
  assert.equal(staticMountForAge(6).id, 'hero-mount-motor-transport');
  assert.equal(staticMountForAge(7).id, 'hero-mount-future-transport');
});

test('painted overlap is remeasured from the part pixels', () => {
  const check = spawn('python', ['scripts/code_ready_measurements.py', '--check'], { stdio: ['ignore', 'pipe', 'pipe'] });
  return new Promise((resolve, reject) => {
    let text = '';
    check.stdout.on('data', chunk => { text += chunk; });
    check.stderr.on('data', chunk => { text += chunk; });
    check.on('exit', code => {
      if (code === 0 && text.includes('passed')) resolve();
      else reject(new Error(text || 'overlap check failed'));
    });
  });
});
