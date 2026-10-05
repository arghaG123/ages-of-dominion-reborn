// The armed control is the one that received pointerdown. A later layout tick must not retarget it.
export function armedChoice(armedId, releasedId) {
  if (armedId) return armedId;
  return releasedId || null;
}

export function parseChallenge(seedText, code) {
  if (!/^\d+$/.test(String(seedText ?? '').trim())) return { error: 'Seed must be an integer from 0 to 4294967295.' };
  const seed = Number(seedText);
  if (!Number.isInteger(seed) || seed < 0 || seed > 0xffffffff) return { error: 'Seed must be an integer from 0 to 4294967295.' };
  const trimmed = String(code ?? '').trim();
  if (!trimmed || trimmed.length > 64) return { error: 'Scenario code must be 1 to 64 characters.' };
  return { seed, code: trimmed };
}
