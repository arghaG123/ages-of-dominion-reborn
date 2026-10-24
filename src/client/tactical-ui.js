// Contextual tactical actions. Choice ids stay stable for the legal engine.
// Column and row labels are 1-based. Cell coordinates in choice ids stay 0-based.

export function defaultIntent(legal, spellCount) {
  if (legal.moves.length) return 'move';
  if (legal.melee.length) return 'melee';
  if (legal.ranged.length) return 'shoot';
  if (spellCount > 0) return 'spell';
  return 'defend';
}

export function keepIntent(intent, legal, spellCount, waited, bonus = false) {
  if (bonus && (intent === 'wait' || intent === 'skip-bonus')) return intent === 'skip-bonus' ? 'skip-bonus' : defaultIntent(legal, spellCount);
  if (intent === 'move' && legal.moves.length) return intent;
  if (intent === 'melee' && legal.melee.length) return intent;
  if (intent === 'shoot' && legal.ranged.length) return intent;
  if (intent === 'spell' && spellCount > 0) return intent;
  if (intent === 'wait' && !waited && !bonus) return intent;
  if (intent === 'defend' || intent === 'auto' || intent === 'retreat') return intent;
  return defaultIntent(legal, spellCount);
}

export function spellAvailability({ spells = 0, castThisRound = false, mana = null, minSpellMana = null, minSpellCost = null, knownSpells = null } = {}) {
  const knownCount = Array.isArray(knownSpells) ? knownSpells.length : knownSpells;
  const minMana = Number.isFinite(minSpellMana) ? minSpellMana : Number.isFinite(minSpellCost) ? minSpellCost : null;
  if (spells > 0) {
    return {
      enabled: true,
      reason: 'available',
      detail: `${spells} ${spells === 1 ? 'cast' : 'casts'} · 1/round`,
    };
  }
  if (castThisRound) {
    return {
      enabled: false,
      reason: 'round-used',
      detail: 'Round cast used (1/round)',
    };
  }
  if (Number.isFinite(knownCount) && knownCount <= 0) {
    return {
      enabled: false,
      reason: 'no-known-spell',
      detail: 'No known spell',
    };
  }
  if (Number.isFinite(mana) && Number.isFinite(minMana) && mana < minMana) {
    return {
      enabled: false,
      reason: 'insufficient-mana',
      detail: `Insufficient mana (${mana}/${minMana})`,
    };
  }
  if (!Number.isFinite(minMana) && Number.isFinite(mana) && mana <= 0) {
    return {
      enabled: false,
      reason: 'insufficient-mana',
      detail: 'Insufficient mana (0)',
    };
  }
  if (knownCount != null || mana != null) {
    return {
      enabled: false,
      reason: 'no-target',
      detail: 'No legal spell target',
    };
  }
  return {
    enabled: false,
    reason: 'unavailable',
    detail: 'No cast available (1/round)',
  };
}

export function battleSpellAvailability(battle, spellsDict = {}) {
  const known = Object.entries(spellsDict || {}).filter(([, spell]) => spell && (spell.lv == null || spell.lv <= 1 + (battle?.wisdom || 0)));
  const knownSpells = known.length;
  const minSpellMana = known.length ? Math.min(...known.map(([, spell]) => spell.mana ?? spell.cost ?? 0)) : null;
  const mana = Number.isFinite(battle?.mana) ? battle.mana : 0;
  const castThisRound = Boolean(battle?.castThisRound);
  const offers = [];
  if (!castThisRound && Array.isArray(battle?.stacks)) {
    for (const [spellId, spell] of known) {
      const cost = spell.mana ?? spell.cost ?? 0;
      if (cost > mana) continue;
      const hostile = spell.type === 'dmg' || spell.type === 'aoe' || spell.type === 'debuff';
      for (const target of battle.stacks) {
        if (!target || target.dead || (target.count != null && target.count <= 0) || (hostile ? target.side !== 'e' : target.side !== 'p')) continue;
        offers.push({ spellId, spell, target });
      }
    }
  }
  const state = spellAvailability({
    spells: offers.length,
    castThisRound,
    mana,
    minSpellMana,
    knownSpells,
  });
  return {
    ...state,
    offers,
    knownSpells,
    minSpellMana,
    mana,
    castThisRound,
  };
}

export function tacticalHeroPlaqueCopy({ className = 'Hero', classTitle = null, level = 1, xp = 0, stats = { atk: 0, def: 0, pow: 0, kno: 0 }, mana = null, morale = 0 } = {}) {
  const roleLabel = classTitle || className || 'Hero';
  const hasMana = Number.isFinite(mana);
  const manaValue = hasMana ? Math.max(0, mana) : null;
  const moralePoints = Number.isFinite(morale) ? morale : 0;
  const experienceText = `XP ${xp}${hasMana ? ` · Mana ${manaValue}` : ''}`;
  return {
    ariaLabel: `${roleLabel}, level ${level}, ${xp} experience. Attack ${stats.atk}, defense ${stats.def}, power ${stats.pow}, knowledge ${stats.kno}${hasMana ? `, battle mana ${manaValue}` : ''}.`,
    identityText: `${roleLabel} · Level ${level}`,
    experienceText,
    subtext: experienceText,
    commandStatsText: `ATK ${stats.atk} · DEF ${stats.def} · PWR ${stats.pow} · KNO ${stats.kno}`,
    moraleText: `Morale ${moralePoints.toFixed(1)} · ${(Math.max(0, moralePoints) * 4.2).toFixed(1)}% bonus chance`,
  };
}

export function modeRows({ moves, melee, ranged, spells, waited, bonus = false, castThisRound = false, mana = null, minSpellMana = null, minSpellCost = null, knownSpells = null }) {
  const spellState = spellAvailability({ spells, castThisRound, mana, minSpellMana, minSpellCost, knownSpells });
  const rows = [
    { id: 'move', label: 'Move', enabled: moves.length > 0, detail: moves.length ? `${moves.length} open cells` : 'No open cell' },
    { id: 'melee', label: 'Melee', enabled: melee.length > 0, detail: melee.length ? `${melee.length} in reach` : 'None in reach' },
    { id: 'shoot', label: 'Shoot', enabled: ranged.length > 0, detail: ranged.length ? `${ranged.length} in range` : 'No shot' },
    { id: 'spell', label: 'Spell', enabled: spellState.enabled, detail: spellState.detail, reason: spellState.reason },
    { id: 'defend', label: 'Defend', enabled: true, detail: 'Brace this stack' },
    { id: 'wait', label: 'Wait', enabled: !waited && !bonus, detail: bonus ? 'Wait is unavailable during a bonus action' : waited ? 'Already waited' : 'Act later this round' },
    { id: 'auto', label: 'Auto', enabled: true, detail: 'Resolve legal actions' },
    { id: 'retreat', label: 'Retreat', enabled: true, detail: 'Leave this battle' },
  ];
  if (bonus) rows.push({ id: 'skip-bonus', label: 'Skip bonus', enabled: true, detail: 'End the extra action' });
  return rows;
}

export function primaryModeRows({ melee, ranged, spells, waited, bonus = false, castThisRound = false, mana = null, minSpellMana = null, minSpellCost = null, knownSpells = null }) {
  const attackTargets = melee.length + ranged.length;
  const spellState = spellAvailability({ spells, castThisRound, mana, minSpellMana, minSpellCost, knownSpells });
  return [
    { id: 'attack', label: 'Attack', enabled: attackTargets > 0, detail: attackTargets ? `${attackTargets} legal targets` : 'No attack in reach' },
    { id: 'defend', label: 'Defend', enabled: true, detail: 'Brace this stack' },
    bonus
      ? { id: 'skip-bonus', label: 'Skip bonus', enabled: true, detail: 'End the extra action' }
      : { id: 'wait', label: 'Wait', enabled: !waited, detail: waited ? 'Already waited' : 'Act later this round' },
    { id: 'spell', label: 'Spell', enabled: spellState.enabled, detail: spellState.detail, reason: spellState.reason },
  ];
}

export function secondaryModeRows({ moves }) {
  return [
    { id: 'move', label: 'Move', enabled: moves.length > 0, detail: moves.length ? `${moves.length} open cells` : 'No open cell' },
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

export function intentSentence(intent, stackTitle, spellContext = null) {
  const who = stackTitle || 'This stack';
  if (intent === 'move') return `${who} can step onto a highlighted cell. Choose the cell here or on the map.`;
  if (intent === 'melee') return `${who} can strike one listed target. Reach includes one legal step when the strike needs it.`;
  if (intent === 'shoot') return `${who} can shoot one listed target.`;
  if (intent === 'spell') {
    const resolved = spellContext && typeof spellContext.reason === 'string'
      ? spellContext
      : spellContext
        ? spellAvailability(spellContext)
        : null;
    if (resolved && !resolved.enabled) {
      if (resolved.reason === 'round-used') return 'Round cast used: your hero already used this round’s spell allowance (1 cast per battle round).';
      if (resolved.reason === 'insufficient-mana') return `Cannot cast: ${resolved.detail.toLowerCase()}. Your hero casts once per battle round.`;
      if (resolved.reason === 'no-known-spell') return 'Cannot cast: no known spell at current Wisdom. Your hero casts once per battle round.';
      if (resolved.reason === 'no-target') return 'Cannot cast: no legal target for affordable spells. Your hero casts once per battle round.';
    }
    return 'Choose one listed cast. Your hero casts once per battle round.';
  }
  if (intent === 'defend') return `${who} braces and ends this action.`;
  if (intent === 'wait') return `${who} can wait once, then act later this round. Wait does not roll morale.`;
  if (intent === 'skip-bonus') return 'Skip ends this bonus action. It does not roll morale again, and it does not restore a spell, a shot, or retaliation.';
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

// Inert markup does not stop HTMLElement.click(). Background dispatch stays closed while Retreat is armed.
export function retreatBlocksBackground({ retreatArmed, inDialog = false }) {
  return Boolean(retreatArmed) && !inDialog;
}

// A redraw may observe a requested screen. An open Retreat battle stays on Tactical until Cancel or Confirm.
export function viewDuringRetreat(requested, { retreatArmed, battleActive }) {
  if (retreatArmed && battleActive && requested !== 'tactical') return 'tactical';
  return requested;
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
