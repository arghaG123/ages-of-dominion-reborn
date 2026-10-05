import { adoptProgress, validate } from './campaign.js';
export const SAVE_KEY = 'aod-reborn-v1';
export const VIEW_KEY = SAVE_KEY + '-view';
export function rememberView(storage, name, screens) {
  if (!screens.includes(name)) throw new Error('Unknown screen');
  storage.setItem(VIEW_KEY, name);
}
export function rememberedView(storage, screens) {
  const name = storage.getItem(VIEW_KEY);
  return screens.includes(name) ? name : 'kingdom';
}
export function checksum(text) {
  let hash = 2166136261;
  for (let i = 0; i < text.length; i++) hash = Math.imul(hash ^ text.charCodeAt(i), 16777619);
  return (hash >>> 0).toString(16).padStart(8, '0');
}
export function encode(state, data) { validate(state, data); const payload = JSON.stringify(state); return JSON.stringify({ schema: 1, payload, checksum: checksum(payload) }); }
export function decode(text, data) {
  const envelope = JSON.parse(text);
  if (envelope.schema !== 1) throw new Error('Unsupported save envelope');
  if (typeof envelope.payload !== 'string' || checksum(envelope.payload) !== envelope.checksum) throw new Error('Damaged save checksum');
  const s = JSON.parse(envelope.payload); adoptProgress(s, data); validate(s, data); return s;
}
function keepDamaged(storage, bytes) {
  if (bytes == null || storage.getItem(SAVE_KEY + '-damaged') != null) return;
  storage.setItem(SAVE_KEY + '-damaged', bytes);
}
function clearStaged(storage) {
  // Removable staging debt after a durable live commit. Failure here must not undo success.
  try { storage.removeItem(SAVE_KEY + '-staged'); }
  catch { /* Staged cleanup is retryable; live bytes already verified. */ }
}
function commit(storage, state, data, replace) {
  const encoded = encode(state, data), previous = storage.getItem(SAVE_KEY);
  let promote = null;
  if (previous !== null) {
    try {
      const previousState = decode(previous, data);
      if (!replace && previousState.revision > state.revision) throw new Error('Refuse stale save revision');
      promote = previous;
    } catch (error) {
      if (error.message === 'Refuse stale save revision') throw error;
      keepDamaged(storage, previous);
    }
  }
  let promoted = false;
  try {
    storage.setItem(SAVE_KEY + '-staged', encoded);
    if (storage.getItem(SAVE_KEY + '-staged') !== encoded) throw new Error('Staged save verification failed');
    decode(storage.getItem(SAVE_KEY + '-staged'), data);
    if (promote !== null) {
      storage.setItem(SAVE_KEY + '-backup', promote);
      promoted = true;
      if (storage.getItem(SAVE_KEY + '-backup') !== promote) throw new Error('Backup promotion failed');
    }
    storage.setItem(SAVE_KEY, encoded);
    if (storage.getItem(SAVE_KEY) !== encoded) throw new Error('Live save verification failed');
  } catch (error) {
    // Live replacement failed. Keep the promoted previous campaign in backup — rolling it
    // back to older bookkeeping would destroy the latest valid recoverable bytes.
    if (promoted) {
      const liveNow = storage.getItem(SAVE_KEY);
      if (liveNow != null && liveNow !== encoded && liveNow !== promote) keepDamaged(storage, liveNow);
    }
    // Leave the verified staged copy when live is not the encoded payload so recovery still has it.
    if (storage.getItem(SAVE_KEY) === encoded) clearStaged(storage);
    throw error;
  }
  clearStaged(storage);
}
export function load(storage, data) {
  const live = storage.getItem(SAVE_KEY);
  if (live === null) return { status: 'EMPTY', state: null };
  try { return { status: 'VALID', state: decode(live, data) }; }
  catch (error) {
    let backup = null;
    try { const raw = storage.getItem(SAVE_KEY + '-backup'); if (raw) backup = decode(raw, data); } catch { /* A damaged backup cannot become a new game. */ }
    return { status: 'DAMAGED', error: error.message, backup, state: null };
  }
}
export function save(storage, state, data) { commit(storage, state, data, false); }
export function replaceCampaign(storage, state, data) {
  const previous = storage.getItem(SAVE_KEY);
  let floor = -1;
  if (previous != null) {
    try { floor = decode(previous, data).revision; } catch { /* A damaged live save does not set the revision floor. */ }
  }
  const next = structuredClone(state);
  if (floor >= next.revision) next.revision = floor + 1;
  commit(storage, next, data, true);
  return next;
}
export function restoreBackup(storage, data) {
  const raw = storage.getItem(SAVE_KEY + '-backup');
  if (!raw) throw new Error('No valid backup');
  const state = decode(raw, data);
  const live = storage.getItem(SAVE_KEY);
  if (live != null && live !== raw) {
    try {
      decode(live, data);
      throw new Error('Live save is valid');
    } catch (error) {
      if (error.message === 'Live save is valid') throw error;
      keepDamaged(storage, live);
    }
  }
  storage.setItem(SAVE_KEY, raw);
  if (storage.getItem(SAVE_KEY) !== raw) throw new Error('Backup restore failed');
  return state;
}
export function slotKey(index) {
  if (!Number.isInteger(index) || index < 1 || index > 3) throw new Error('Invalid save slot');
  return `${SAVE_KEY}-slot-${index}`;
}
export function storeSlot(storage, index, state, data) {
  const encoded = encode(state, data);
  storage.setItem(slotKey(index), encoded);
  if (storage.getItem(slotKey(index)) !== encoded) throw new Error('Slot verification failed');
}
export function loadSlot(storage, index, data) {
  const raw = storage.getItem(slotKey(index));
  return raw == null ? null : decode(raw, data);
}
