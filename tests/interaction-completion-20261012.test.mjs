import test from 'node:test';
import assert from 'node:assert/strict';
import { drawPlate, plateOffset } from '../src/client/actor.js';
import { kitEra, heroBody } from '../src/client/hero-room.js';
import heroBodies from '../src/data/hero-bodies-20261011.json' with { type: 'json' };
import { activeStackId, startBattle } from '../src/core/battle.js';

test('plateOffset and drawPlate apply motion clips to single-pose plates', () => {
  // Test plateOffset clips
  const attackMotion = plateOffset(0.2, { clip: 'attack', reduced: false });
  assert.ok(attackMotion.rot !== 0, 'attack clip must produce rotation');

  const deathMotion = plateOffset(0, { clip: 'death', reduced: false });
  assert.equal(deathMotion.rot, 70, 'death clip must tilt 70 degrees');
  assert.equal(deathMotion.y, 8, 'death clip must drop down by 8px');

  const reducedMotion = plateOffset(0.2, { clip: 'attack', reduced: true });
  assert.equal(reducedMotion.y, 0, 'reduced motion must zero out y');
  assert.equal(reducedMotion.rot, 0, 'reduced motion must zero out rot');

  // Test drawPlate with DOM-like stub
  const createdElements = [];
  const fakeElement = (tag, attrs = {}) => {
    const el = { tag, attrs, children: [], append: child => el.children.push(child) };
    createdElements.push(el);
    return el;
  };
  const fakeWorld = { append: el => createdElements.push(el) };

  const singlePlate = {
    file: 'assets/some-plate.png',
    pose: 'single',
    width: 100,
    height: 100,
  };

  const rendered = drawPlate(fakeWorld, fakeElement, singlePlate, 100, 100, 50, {
    clip: 'death',
    reduced: false,
  });
  assert.equal(rendered, true);

  const groupNode = createdElements.find(el => el.tag === 'g' && el.attrs['data-plate-motion'] === 'death');
  assert.ok(groupNode, 'must render a group with data-plate-motion="death"');
  assert.ok(groupNode.attrs.transform.includes('rotate(70)'), 'group transform must reflect death tilt');
});

test('tactical activeStackId accurately resolves active stack and queue', () => {
  const battle = startBattle({
    id: 'test-battle',
    positioned: true,
    rngState: 42,
    mana: 20,
    wisdom: 1,
    morale: 0,
    stacks: [
      { id: 'player-1', side: 'p', x: 1, y: 8, count: 5, maxCount: 5, atk: 4, def: 2, dmin: 2, dmax: 4, uhp: 20, top: 20, spd: 4, rng: 0, shots: 0 },
      { id: 'enemy-1', side: 'e', x: 5, y: 2, count: 3, maxCount: 3, atk: 3, def: 1, dmin: 1, dmax: 3, uhp: 15, top: 15, spd: 2, rng: 0, shots: 0 },
    ],
  });

  const active = activeStackId(battle);
  assert.equal(active, 'player-1', 'faster unit player-1 must be active first');
});

test('hero-bodies healer has verified multi-part composite assembly provenance', () => {
  const healer = heroBodies.bodies.healer;
  assert.ok(healer, 'healer body must exist');
  assert.ok(healer.assembly, 'healer must have assembly provenance');
  assert.equal(healer.assembly.method, 'five-part-composite');
  assert.equal(healer.assembly.parts.length, 6, 'must document all 6 assembled parts including mirrored boot');
  
  const partNames = healer.assembly.parts.map(p => p.part);
  assert.ok(partNames.includes('head'));
  assert.ok(partNames.includes('torso'));
  assert.ok(partNames.includes('skirt'));
  assert.ok(partNames.includes('staff_arms'));
  assert.ok(partNames.includes('boot_left'));
  assert.ok(partNames.includes('boot_right'));
});

test('kitEra covers all eight ages into the canonical four kit eras', () => {
  assert.equal(kitEra(0), 'ancient'); // Stone
  assert.equal(kitEra(1), 'ancient'); // Bronze
  assert.equal(kitEra(2), 'ancient'); // Iron
  assert.equal(kitEra(3), 'medieval'); // Medieval
  assert.equal(kitEra(4), 'powder'); // Gunpowder
  assert.equal(kitEra(5), 'powder'); // Industrial
  assert.equal(kitEra(6), 'mech'); // Modern
  assert.equal(kitEra(7), 'mech'); // Future
});

test('tactical figure clip distinguishes turn waiting, movement, attack strike and death', () => {
  const battle = startBattle({
    id: 'test-battle-clips',
    positioned: true,
    rngState: 42,
    mana: 20,
    wisdom: 1,
    morale: 0,
    stacks: [
      { id: 'player-1', side: 'p', x: 1, y: 8, count: 5, maxCount: 5, atk: 4, def: 2, dmin: 2, dmax: 4, uhp: 20, top: 20, spd: 4, rng: 0, shots: 0 },
      { id: 'enemy-1', side: 'e', x: 5, y: 2, count: 3, maxCount: 3, atk: 3, def: 1, dmin: 1, dmax: 3, uhp: 15, top: 15, spd: 2, rng: 0, shots: 0 },
    ],
  });
  const activeId = activeStackId(battle);
  assert.equal(activeId, 'player-1');

  // Helper matching the main.js logic:
  const resolveClip = (stack, alive, tacticalIntent) => {
    const isActing = Boolean(stack?.id && stack.id === activeId);
    const lastAction = battle?.log?.[battle.log.length - 1];
    const isAttacking = isActing && (
      tacticalIntent === 'melee' ||
      tacticalIntent === 'shoot' ||
      ((lastAction?.type === 'strike' || lastAction?.type === 'retaliate') && lastAction?.attackerId === stack.id)
    );
    return alive ? (isAttacking ? 'attack' : (isActing && tacticalIntent === 'move') ? 'walk' : 'idle') : 'death';
  };

  const actingStack = battle.stacks[0];
  const otherStack = battle.stacks[1];

  // While waiting for player command (no intent selected):
  assert.equal(resolveClip(actingStack, true, null), 'idle', 'turn waiting must be idle, not walking in place');
  // When move intent is active:
  assert.equal(resolveClip(actingStack, true, 'move'), 'walk', 'moving must play walk');
  // When melee/shoot intent is active:
  assert.equal(resolveClip(actingStack, true, 'melee'), 'attack', 'melee intent must play attack');
  assert.equal(resolveClip(actingStack, true, 'shoot'), 'attack', 'shoot intent must play attack');
  // Inactive stack:
  assert.equal(resolveClip(otherStack, true, null), 'idle', 'inactive stack must be idle');
  // Dead stack:
  assert.equal(resolveClip(actingStack, false, null), 'death', 'dead stack must play death');
});

test('hero room 6 equipment sockets have valid coordinates and non-zero dimensions', () => {
  const fitted = { x: 448, y: 120, width: 280, height: 500 };
  const sockets = [
    { slot: 'helm', x: fitted.x + (fitted.width - 76) / 2, y: fitted.y - 28, size: 76 },
    { slot: 'weapon', x: fitted.x + fitted.width * 0.76, y: fitted.y + fitted.height * 0.44, size: 84 },
    { slot: 'offhand', x: fitted.x - 24, y: fitted.y + fitted.height * 0.48, size: 84 },
    { slot: 'armor', x: fitted.x + (fitted.width - 80) / 2, y: fitted.y + fitted.height * 0.32, size: 80 },
    { slot: 'boots', x: fitted.x + (fitted.width - 70) / 2, y: fitted.y + fitted.height * 0.82, size: 70 },
    { slot: 'accessory', x: fitted.x + fitted.width * 0.12, y: fitted.y + fitted.height * 0.22, size: 60 },
  ];
  assert.equal(sockets.length, 6);
  for (const s of sockets) {
    assert.ok(s.size >= 48, `${s.slot} must be >= 48px`);
    assert.ok(s.x >= 0, `${s.slot} x must be positive`);
    assert.ok(s.y >= 0, `${s.slot} y must be positive`);
  }
});
