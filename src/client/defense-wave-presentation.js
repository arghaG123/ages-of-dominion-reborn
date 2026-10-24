export function defenseWaveLabel(session) {
  const total = Number.isSafeInteger(session?.waves) && session.waves > 0 ? session.waves : 0;
  const cleared = Number.isSafeInteger(session?.clearedWaves) && session.clearedWaves >= 0 ? session.clearedWaves : 0;
  if (!total) return 'Wave unavailable';
  const active = session.status === 'ACTIVE' && !session.pendingSettlement;
  const number = Math.min(total, cleared + (active ? 1 : 0));
  return active ? `Wave ${number} of ${total}` : `Waves cleared ${number} of ${total}`;
}
