import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { command, newCampaign } from '../src/core/campaign.js';
import { advanceDefense, createDefense } from '../src/core/defense.js';

const fresh = () => newCampaign(contract, data, 1_700_000_000_000, 123456789);
const act = (state, id, type, payload, now) => command(state, { id, type, payload }, now ?? state.clock, data);

function play(session, seconds = 120) {
  let current = session;
  let hits = 0;
  const hp = new Map(current.queue.map(enemy => [enemy.id, enemy.hp]));
  let steps = 0;
  while (current.status === 'ACTIVE' && steps < seconds * 4) {
    current = advanceDefense(current, 0.25, { speed: 1 });
    for (const enemy of current.queue) {
      const before = hp.get(enemy.id);
      if (before != null && enemy.hp < before && !enemy.leaked) hits += 1;
      hp.set(enemy.id, enemy.hp);
    }
    steps += 1;
  }
  return { session: current, hits };
}

test('starter towers fire inside their range and an undeployed siege still loses', () => {
  let state = act(fresh(), 'siege', 'START_SIEGE');
  const played = play(state.defense, 80);
  assert.ok(played.hits > 0, 'towers never damaged an attacker');
  assert.equal(played.session.status, 'RESOLVED');
  assert.equal(played.session.winner, 'e');
  assert.equal(played.session.clearedWaves, 0);
  assert.ok(played.session.core <= 0);
});

test('grouped archers do not freeze outside a dead tower', () => {
  const session = createDefense(fresh(), data, { practice: 'siege', waves: 1 });
  session.towers.forEach(tower => { tower.hp = 0; });
  for (const enemy of session.queue) {
    enemy.role = 'archer';
    enemy.hp = 40;
    enemy.spawned = true;
    enemy.progress = 0.4;
    enemy.spawnAt = 0;
    enemy.leaked = false;
    enemy.attackCooldown = 0;
  }
  session.enemies = session.queue.map(enemy => ({ ...enemy }));
  let next = session;
  for (let step = 0; step < 8; step++) next = advanceDefense(next, 0.25);
  assert.ok(next.queue.every(enemy => enemy.progress > 1.2 || enemy.leaked));
});

test('a workshop and a splash tower make the starter siege winnable', () => {
  let now = 1_700_000_000_000;
  let state = fresh();
  let n = 0;
  const go = (type, payload, delay = 0) => {
    now += delay;
    state = command(state, { id: `prep-${n++}`, type, payload }, now, data);
  };
  const empty = () => state.plots.find(plot => plot.type == null).id;
  go('BUILD', { plotId: empty(), building: 'lumber' });
  go('BUILD', { plotId: empty(), building: 'farm' });
  go('BUILD', { plotId: empty(), building: 'quarry' });
  go('BUILD', { plotId: empty(), building: 'barracks' }, 8000);
  for (let i = 0; i < 40 && !state.towers.some(tower => tower.fam === 'splash'); i++) {
    const workshop = state.plots.find(plot => plot.type === 'workshop');
    if (!workshop && state.resources.wood >= 70 && state.resources.stone >= 95) go('BUILD', { plotId: empty(), building: 'workshop' }, 1000);
    else if (workshop?.level >= 1 && state.resources.wood >= 80 && state.resources.stone >= 90 && state.resources.gold >= 45) go('BUY_TOWER', { family: 'splash' }, 1000);
    else go('END_DAY', {}, 15000);
  }
  assert.ok(state.towers.some(tower => tower.fam === 'splash'));
  go('START_SIEGE', {});
  go('DEPLOY_DEFENSE', {});
  go('DEPLOY_ARMY', { stackId: 'army-1' });
  const played = play(state.defense, 160);
  assert.equal(played.session.status, 'RESOLVED');
  assert.equal(played.session.winner, 'p');
  assert.ok(played.session.clearedWaves >= 3);
  assert.ok(played.session.towers.find(tower => tower.fam === 'splash').hp > 0);
});
