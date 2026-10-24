import test from 'node:test';
import assert from 'node:assert/strict';
import {
  SPELL_CATEGORIES,
  activeCommittedFeedback,
  committedBattleEvents,
  motionFor,
  spellEffectCategory,
} from '../src/client/committed-motion.js';
import { clipAngles, plateOffset } from '../src/client/actor.js';
import { paintedPose } from '../src/client/anatomy.js';

test('strike survives queue advancement, retaliation and a trailing morale log', () => {
  const before = { id:'b', log:[], stacks:[{id:'p',x:0,y:0},{id:'e',x:1,y:0}] };
  const after = { ...before, queue:['e'], log:[{type:'strike',attackerId:'p',defenderId:'e'},
    {type:'retaliate',attackerId:'e',defenderId:'p'},{type:'morale',id:'p'}] };
  const events = committedBattleEvents(before, after, 'command-1', 10);
  assert.equal(events.length,2);
  assert.equal(motionFor(events,'b','p',10.1).clip,'attack');
  assert.equal(motionFor(events,'b','p',10.7).clip,'hit');
  assert.equal(motionFor(events,'b','e',10.7).clip,'attack');
  assert.equal(motionFor(events,'b','p',12),null);
  assert.equal(motionFor(events,'b','p',10.1,true),null);
  assert.equal(motionFor(events,'another-session','p',10.1),null);
});
test('capped logs and committed move use before position and unique command identity', () => {
  const before={id:'b',log:[{type:'wait',id:'old'},{type:'defend',id:'p'}],stacks:[{id:'p',x:2,y:3}]};
  const after={...before,log:[{type:'defend',id:'p'},{type:'move',id:'p',to:[3,4]}],stacks:[{id:'p',x:3,y:4}]};
  const [event]=committedBattleEvents(before,after,'command-2',20);
  assert.deepEqual(event.from,[2,3]);
  assert.deepEqual(event.to,[3,4]);
  assert.match(event.eventId,/command-2/);
  assert.deepEqual(committedBattleEvents(after,after,'preview',21),[]);
});

test('all 8 spells preserve spellId and map to damage, buff, heal, or debuff presentation categories', () => {
  assert.equal(Object.keys(SPELL_CATEGORIES).length, 8);
  assert.equal(spellEffectCategory('arrow'), 'damage');
  assert.equal(spellEffectCategory('bolt'), 'damage');
  assert.equal(spellEffectCategory('fireball'), 'damage');
  assert.equal(spellEffectCategory('bless'), 'buff');
  assert.equal(spellEffectCategory('haste'), 'buff');
  assert.equal(spellEffectCategory('cure'), 'heal');
  assert.equal(spellEffectCategory('resurrect'), 'heal');
  assert.equal(spellEffectCategory('slow'), 'debuff');
});

test('beneficial and debuff spells never assign hit or death reactions, including self-target casts', () => {
  const baseStacks = [
    { id: 'p1', side: 'player', x: 1, y: 1, hp: 30, maxHp: 50, count: 4, startCount: 5, fallen: 1 },
    { id: 'p2', side: 'player', x: 1, y: 3, hp: 20, maxHp: 40, count: 2, startCount: 4, fallen: 2 },
    { id: 'e1', side: 'enemy', x: 6, y: 2, hp: 45, maxHp: 45, count: 3, startCount: 3, fallen: 0 },
  ];

  for (const [spellId, targetId, expectedClip] of [
    ['bless', 'p2', 'buff'],
    ['haste', 'p2', 'buff'],
    ['cure', 'p2', 'heal'],
    ['resurrect', 'p2', 'heal'],
    ['slow', 'e1', 'debuff'],
  ]) {
    const before = { id: 'b-spells', log: [], stacks: baseStacks };
    const afterStacks = baseStacks.map(stack => {
      if (stack.id !== targetId) return { ...stack };
      if (spellId === 'cure') return { ...stack, hp: 40 };
      if (spellId === 'resurrect') return { ...stack, hp: 40, count: 3, fallen: 1 };
      return { ...stack };
    });
    const after = {
      ...before,
      stacks: afterStacks,
      log: [{ type: 'spell', id: spellId, casterId: 'p1', targetId }],
    };
    const events = committedBattleEvents(before, after, `cmd-${spellId}`, 30);
    assert.equal(events.length, 1);
    assert.equal(events[0].spellId, spellId);
    assert.equal(events[0].effectCategory, expectedClip);
    assert.equal(events[0].selfTarget, false);

    const casterMotion = motionFor(events, 'b-spells', 'p1', 30.2);
    const targetMotion = motionFor(events, 'b-spells', targetId, 30.2);
    assert.equal(casterMotion.clip, 'cast');
    assert.equal(casterMotion.spellId, spellId);
    assert.equal(targetMotion.clip, expectedClip);
    assert.equal(targetMotion.spellId, spellId);
    assert.notEqual(targetMotion.clip, 'hit');
    assert.notEqual(targetMotion.clip, 'death');
  }

  // Self-target (casterId === targetId) retains readable casting AND target feedback
  for (const [spellId, expectedTargetClip] of [
    ['bless', 'buff'],
    ['haste', 'buff'],
    ['cure', 'heal'],
    ['resurrect', 'heal'],
  ]) {
    const before = { id: 'b-self', log: [], stacks: baseStacks };
    const after = {
      ...before,
      stacks: baseStacks.map(s => (s.id === 'p1' ? { ...s, hp: 50, count: 5, fallen: 0 } : { ...s })),
      log: [{ type: 'spell', id: spellId, casterId: 'p1', targetId: 'p1' }],
    };
    const events = committedBattleEvents(before, after, `self-${spellId}`, 40);
    assert.equal(events.length, 1);
    assert.equal(events[0].selfTarget, true);
    const selfMotion = motionFor(events, 'b-self', 'p1', 40.2);
    assert.equal(selfMotion.clip, 'cast');
    assert.equal(selfMotion.targetClip, expectedTargetClip);
    assert.equal(selfMotion.role, 'self-cast');
    assert.equal(selfMotion.selfTarget, true);
    assert.notEqual(selfMotion.clip, 'hit');
    assert.notEqual(selfMotion.clip, 'death');
    assert.notEqual(selfMotion.targetClip, 'hit');
    assert.notEqual(selfMotion.targetClip, 'death');
  }
});

test('offensive spells preserve hit and death reactions, including fireball AoE splash targets', () => {
  const before = {
    id: 'b-offense',
    log: [],
    stacks: [
      { id: 'p1', side: 'player', x: 1, y: 2, hp: 40, count: 4 },
      { id: 'e1', side: 'enemy', x: 6, y: 2, hp: 18, count: 1 },
      { id: 'e2', side: 'enemy', x: 6, y: 3, hp: 35, count: 3 },
      { id: 'e3', side: 'enemy', x: 8, y: 5, hp: 35, count: 3 },
    ],
  };
  const after = {
    ...before,
    stacks: [
      { id: 'p1', side: 'player', x: 1, y: 2, hp: 32, count: 4 },
      { id: 'e1', side: 'enemy', x: 6, y: 2, hp: 0, count: 0 },
      { id: 'e2', side: 'enemy', x: 6, y: 3, hp: 11, count: 2 },
      { id: 'e3', side: 'enemy', x: 8, y: 5, hp: 20, count: 2 },
    ],
    log: [{ type: 'spell', id: 'fireball', casterId: 'p1', targetId: 'e1', damage: 24 }],
  };
  const events = committedBattleEvents(before, after, 'cmd-fireball', 50);
  assert.equal(events.length, 1);
  assert.equal(events[0].spellId, 'fireball');
  assert.equal(events[0].effectCategory, 'damage');
  assert.equal(events[0].targetDied, true);
  assert.deepEqual(events[0].affectedTargets.map(t => t.id), ['e1', 'e2']);

  assert.equal(motionFor(events, 'b-offense', 'p1', 50.2).clip, 'cast');
  assert.equal(motionFor(events, 'b-offense', 'e1', 50.2).clip, 'death');
  assert.equal(motionFor(events, 'b-offense', 'e2', 50.2).clip, 'hit');
  assert.equal(motionFor(events, 'b-offense', 'e3', 50.2), null);
});

test('actor clipAngles, plateOffset, and anatomy paintedPose differentiate cast/buff/heal/debuff from hit/death recoil', () => {
  const hitPlate = plateOffset(0.5, { clip: 'hit' });
  const deathPlate = plateOffset(0.5, { clip: 'death' });
  assert.equal(hitPlate.rot, 14);
  assert.equal(deathPlate.rot, 70);

  for (const clip of ['cast', 'buff', 'heal', 'debuff']) {
    const offset = plateOffset(0.5, { clip });
    assert.notEqual(offset.rot, 14, `${clip} plateOffset must not use hit rotation`);
    assert.notEqual(offset.rot, 70, `${clip} plateOffset must not use death rotation`);
    const angles = clipAngles(clip, 0.5);
    assert.notEqual(angles.spine, 26, `${clip} clipAngles must not use hit backward spine recoil`);
    assert.notEqual(angles.spine, 78, `${clip} clipAngles must not use death collapse spine`);
    const pose = paintedPose(clip, 0.5, false);
    assert.notEqual(pose.head, 14, `${clip} paintedPose must not use hit head recoil`);
    assert.notEqual(pose.head, 20, `${clip} paintedPose must not use death head collapse`);
  }
});

test('activeCommittedFeedback returns static latest-action feedback under reducedMotion without enabling animated motionFor', () => {
  const before = { id: 'b-rm', log: [], stacks: [{ id: 'p1', x: 1, y: 1, hp: 20, count: 2 }] };
  const after = {
    ...before,
    stacks: [{ id: 'p1', x: 1, y: 1, hp: 35, count: 2 }],
    log: [{ type: 'spell', id: 'cure', casterId: 'p1', targetId: 'p1' }],
  };
  const events = committedBattleEvents(before, after, 'cmd-rm-1', 100);
  assert.equal(motionFor(events, 'b-rm', 'p1', 100.2, true), null);
  const feedback = activeCommittedFeedback(events, 'b-rm', 105, true);
  assert.equal(feedback.length, 1);
  assert.equal(feedback[0].spellId, 'cure');
  assert.equal(feedback[0].reduced, true);
  assert.deepEqual(activeCommittedFeedback(events, 'other-battle', 105, true), []);
});

