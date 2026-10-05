import cards from '../data/portrait-cards.json' with { type: 'json' };

export function portraitCard(classId, age) {
  const card = cards.cards[classId];
  if (!card || age < card.minAge) return null;
  return card;
}

export function pendingPortrait(classId, age) {
  if (portraitCard(classId, age)) return null;
  const pending = cards.pending?.[classId];
  if (!pending || pending.status !== 'PENDING_CARD_REVIEW') return null;
  if (age >= (cards.cards[classId]?.minAge ?? 99)) return null;
  return pending;
}

export function portraitRejected() {
  return cards.rejected;
}

export { cards };
