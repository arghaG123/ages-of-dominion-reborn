import { validate } from './campaign.js';
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
  const s = JSON.parse(envelope.payload); validate(s, data); return s;
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
export function save(storage, state, data) {
  const encoded = encode(state, data), previous = storage.getItem(SAVE_KEY);
  if (previous !== null) {
    try {
      const previousState = decode(previous, data);
      if (previousState.revision > state.revision) throw new Error('Refuse stale save revision');
    } catch (error) {
      if (error.message === 'Refuse stale save revision') throw error;
      if (storage.getItem(SAVE_KEY + '-damaged') == null) storage.setItem(SAVE_KEY + '-damaged', previous);
    }
  }
  storage.setItem(SAVE_KEY + '-staged', encoded);
  if (storage.getItem(SAVE_KEY + '-staged') !== encoded) throw new Error('Staged save verification failed');
  decode(storage.getItem(SAVE_KEY + '-staged'), data);
  // Backup old valid live before replacing it. A quota failure leaves original live intact.
  if (previous !== null) storage.setItem(SAVE_KEY + '-backup', previous);
  storage.setItem(SAVE_KEY, encoded);
  if (storage.getItem(SAVE_KEY) !== encoded) throw new Error('Live save verification failed');
  storage.removeItem(SAVE_KEY + '-staged');
}
