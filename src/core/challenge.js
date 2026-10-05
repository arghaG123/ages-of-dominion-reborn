// Local duel-v1 exchange. The label is recorded and does not change the roster or map.
import { checksum } from './save.js';
import { createChallengeBattle, playOut } from './battle.js';

export const SCENARIO_ID = 'duel-v1';
export const RULES_REVISION = 'tactical-rules-2026-10-04';
export const CODE_MAX = 480;

export function challengeDescriptor(seed, label) {
  if (!Number.isInteger(seed) || seed < 0 || seed > 0xffffffff) throw new Error('Seed must be an integer from 0 to 4294967295.');
  if (typeof label !== 'string' || label.length < 1 || label.length > 64) throw new Error('Scenario code must be 1 to 64 characters.');
  return { schema: 1, scenarioId: SCENARIO_ID, seed, label };
}

export function validateDescriptor(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return { error: 'Unsupported challenge.' };
  const keys = Object.keys(value).filter(key => key !== 'integrity');
  if (keys.some(key => !['schema', 'scenarioId', 'seed', 'label'].includes(key))) return { error: 'Unsupported challenge.' };
  if (value.schema !== 1) return { error: 'Unsupported challenge schema.' };
  if (value.scenarioId !== SCENARIO_ID) return { error: 'Unsupported challenge scenario.' };
  if (!Number.isInteger(value.seed) || value.seed < 0 || value.seed > 0xffffffff) return { error: 'Seed must be an integer from 0 to 4294967295.' };
  if (typeof value.label !== 'string' || value.label.length < 1 || value.label.length > 64) return { error: 'Scenario code must be 1 to 64 characters.' };
  return { descriptor: { schema: 1, scenarioId: SCENARIO_ID, seed: value.seed, label: value.label } };
}

function encodeBytes(bytes) {
  let bin = '';
  for (const byte of bytes) bin += String.fromCharCode(byte);
  return btoa(bin).replaceAll('+', '-').replaceAll('/', '_').replace(/=+$/, '');
}

function decodeBytes(text) {
  const pad = text.length % 4 === 0 ? '' : '='.repeat(4 - (text.length % 4));
  const bin = atob(text.replaceAll('-', '+').replaceAll('_', '/') + pad);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

export function encodeChallengeCode(descriptor) {
  const checked = validateDescriptor(descriptor);
  if (checked.error) throw new Error(checked.error);
  const body = JSON.stringify(checked.descriptor);
  const packed = JSON.stringify({ ...checked.descriptor, integrity: checksum(body) });
  const code = encodeBytes(new TextEncoder().encode(packed));
  if (code.length > CODE_MAX) throw new Error('Challenge code is too large.');
  return code;
}

export function decodeChallengeCode(text) {
  const raw = String(text ?? '').trim();
  if (!raw) return { error: 'Corrupt challenge code.' };
  if (raw.length > CODE_MAX) return { error: 'Challenge code is too large.' };
  if (!/^[A-Za-z0-9_-]+$/.test(raw)) return { error: 'Corrupt challenge code.' };
  let parsed;
  try { parsed = JSON.parse(new TextDecoder().decode(decodeBytes(raw))); }
  catch { return { error: 'Corrupt challenge code.' }; }
  const integrity = parsed.integrity;
  delete parsed.integrity;
  const checked = validateDescriptor(parsed);
  if (checked.error) return checked;
  if (integrity !== checksum(JSON.stringify(checked.descriptor))) return { error: 'Corrupt challenge code.' };
  return checked;
}

export function challengeResult(battle, descriptor) {
  const checked = validateDescriptor(descriptor);
  if (checked.error) throw new Error(checked.error);
  const survivors = {
    p: battle.stacks.filter(stack => stack.side === 'p' && !stack.dead).reduce((sum, stack) => sum + stack.count, 0),
    e: battle.stacks.filter(stack => stack.side === 'e' && !stack.dead).reduce((sum, stack) => sum + stack.count, 0),
  };
  const actions = (battle.log || []).map(entry => ({
    type: entry.type,
    id: entry.id ?? null,
    to: entry.to ?? null,
    attackerId: entry.attackerId ?? null,
    defenderId: entry.defenderId ?? null,
    damage: entry.damage ?? null,
  }));
  const outcome = battle.outcome ?? null;
  const digest = checksum(JSON.stringify({
    descriptor: checked.descriptor,
    rulesRevision: RULES_REVISION,
    outcome,
    rounds: battle.round,
    survivors,
    actions,
  }));
  return {
    descriptor: checked.descriptor,
    rulesRevision: RULES_REVISION,
    outcome,
    rounds: battle.round,
    survivors,
    actions,
    digest,
  };
}

export function reproduceChallenge(seed, label) {
  const descriptor = challengeDescriptor(seed, label);
  const battle = playOut(createChallengeBattle(seed, label));
  return challengeResult(battle, descriptor);
}
