// Contextual tactical actions. Choice ids stay stable for the legal engine.
// Column and row labels are 1-based. Cell coordinates in choice ids stay 0-based.

export function defaultIntent(legal, spellCount) {
  if (legal.moves.length) return 'move';
  if (legal.melee.length) return 'melee';
  if (legal.ranged.length) return 'shoot';
  if (spellCount > 0) return 'spell';
  return 'defend';
}

export function keepIntent(intent, legal, spellCount, waited) {
  if (intent === 'move' && legal.moves.length) return intent;
  if (intent === 'melee' && legal.melee.length) return intent;
  if (intent === 'shoot' && legal.ranged.length) return intent;
  if (intent === 'spell' && spellCount > 0) return intent;
  if (intent === 'wait' && !waited) return intent;
  if (intent === 'defend' || intent === 'auto' || intent === 'retreat') return intent;
  return defaultIntent(legal, spellCount);
}

export function modeRows({ moves, melee, ranged, spells, waited }) {
  return [
    { id: 'move', label: 'Move', enabled: moves.length > 0, detail: moves.length ? `${moves.length} open cells` : 'No open cell' },
    { id: 'melee', label: 'Melee', enabled: melee.length > 0, detail: melee.length ? `${melee.length} in reach` : 'None in reach' },
    { id: 'shoot', label: 'Shoot', enabled: ranged.length > 0, detail: ranged.length ? `${ranged.length} in range` : 'No shot' },
    { id: 'spell', label: 'Spell', enabled: spells > 0, detail: spells ? `${spells} casts` : 'No cast' },
    { id: 'defend', label: 'Defend', enabled: true, detail: 'Brace this stack' },
    { id: 'wait', label: 'Wait', enabled: !waited, detail: waited ? 'Already waited' : 'Act later this round' },
    { id: 'auto', label: 'Auto', enabled: true, detail: 'Resolve legal actions' },
    { id: 'retreat', label: 'Retreat', enabled: true, detail: 'Leave this battle' },
  ];
}

export function moveLabel(cell) {
  return `Move to column ${cell[0] + 1}, row ${cell[1] + 1}`;
}

export function strikeLabel(kind, title, count) {
  const verb = kind === 'melee' ? 'Strike' : 'Shoot';
  return `${verb} ${title} · ${count} left`;
}

export function spellLabel(name, title, mana) {
  return `${name} on ${title} · ${mana} mana`;
}

export function intentSentence(intent, stackTitle) {
  const who = stackTitle || 'This stack';
  if (intent === 'move') return `${who} can step onto a highlighted cell. Choose the cell here or on the map.`;
  if (intent === 'melee') return `${who} can strike one listed target. Reach includes one legal step when the strike needs it.`;
  if (intent === 'shoot') return `${who} can shoot one listed target.`;
  if (intent === 'spell') return 'Choose one listed cast. A stack casts once this round.';
  if (intent === 'defend') return `${who} braces and ends this action.`;
  if (intent === 'wait') return `${who} can wait once, then act later this round.`;
  if (intent === 'auto') return 'Auto uses the legal engine. It does not invent a result.';
  if (intent === 'retreat') return 'Retreat leaves this battle. Confirm or cancel in the dialog. Cancel spends nothing.';
  return 'Choose Move, Melee, Shoot, Spell, Defend, Wait, Auto or Retreat.';
}

export function retreatFocusTarget({ open, restoreTrigger, activeChoice, triggerChoice = 'retreat' }) {
  if (open) return 'retreat-cancel';
  if (restoreTrigger) return triggerChoice;
  if (activeChoice && activeChoice !== 'retreat-cancel' && activeChoice !== 'retreat-confirm') return activeChoice;
  return '';
}

export function retreatNotice(practice) {
  const campaign = practice === 'campaign';
  return {
    title: 'Retreat from this battle?',
    confirm: 'Confirm retreat',
    cancel: 'Cancel',
    body: campaign
      ? 'Survivors keep the counts they have now. Losses already taken stay. Retreat pays no victory gold, experience, or loot, and grants no rank experience. You return to the place the fight started. The guard stays. Mana becomes the mana left in this battle when the result is applied. Cancel spends no turn, mana, or resources.'
      : 'This practice battle ends with no victory reward. It does not change campaign resources, items, casualties, experience, mana, or story. Cancel spends no turn.',
  };
}

// One gesture, rechecked at release. A redraw may replace the element; the key must still match and still be legal.
export function acceptMapActivation({ armed, released, intent, legal }) {
  if (!armed || !released || armed.key !== released.key || !legal) return null;
  if (armed.kind === 'move' && intent === 'move' && Array.isArray(armed.cell)) {
    const ok = legal.moves.some(cell => cell[0] === armed.cell[0] && cell[1] === armed.cell[1]);
    return ok ? { action: 'move', to: [armed.cell[0], armed.cell[1]] } : null;
  }
  if (armed.kind === 'melee' && intent === 'melee' && legal.melee.includes(armed.id)) return { action: 'melee', targetId: armed.id };
  if (armed.kind === 'shoot' && intent === 'shoot' && legal.ranged.includes(armed.id)) return { action: 'strike', targetId: armed.id };
  return null;
}

export function stackCaption({ title, count, hp, maxHp, action }) {
  const health = `${hp}/${maxHp} hp`;
  const actionText = action ? ` · ${action}` : '';
  return `${title} · ${count} · ${health}${actionText}`;
}
