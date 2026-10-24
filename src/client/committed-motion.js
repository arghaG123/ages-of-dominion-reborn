// Transient presentation, created only after a successful core command. Logs
// provide effects; the before-state keeps the actor even after the queue moves.

export const SPELL_CATEGORIES = Object.freeze({
  arrow: 'damage',
  bolt: 'damage',
  fireball: 'damage',
  bless: 'buff',
  haste: 'buff',
  cure: 'heal',
  resurrect: 'heal',
  slow: 'debuff',
});

function stackPoolHp(stack) {
  if (!stack || stack.dead || (stack.count ?? 0) <= 0) return 0;
  if (Number.isFinite(stack.uhp)) {
    const uhp = stack.uhp;
    const top = stack.top ?? uhp;
    return Math.max(0, (stack.count - 1) * uhp + top);
  }
  if (Number.isFinite(stack.hp)) return Math.max(0, stack.hp);
  return stack.count ?? 0;
}

function stackBecameDead(previousStack, nextStack) {
  if (!nextStack) return false;
  if (nextStack.dead && !previousStack?.dead) return true;
  if ((nextStack.count ?? 1) <= 0 && (previousStack?.count ?? 1) > 0) return true;
  if (Number.isFinite(nextStack.hp) && nextStack.hp <= 0 && (previousStack?.hp ?? 1) > 0) return true;
  return false;
}

export function spellEffectCategory(spellId, previousTarget = null, target = null, caster = null) {
  if (spellId && SPELL_CATEGORIES[spellId]) return SPELL_CATEGORIES[spellId];
  if (previousTarget && target) {
    const prevHp = stackPoolHp(previousTarget);
    const nextHp = stackPoolHp(target);
    if (nextHp > prevHp || (target.count ?? 0) > (previousTarget.count ?? 0)) return 'heal';
    if (nextHp < prevHp || stackBecameDead(previousTarget, target)) return 'damage';
    if ((target.blessCounter || 0) > (previousTarget.blessCounter || 0) || (target.hasteCounter || 0) > (previousTarget.hasteCounter || 0)) return 'buff';
    if ((target.slowCounter || 0) > (previousTarget.slowCounter || 0)) return 'debuff';
  }
  if (caster?.side && target?.side) return caster.side === target.side ? 'buff' : 'damage';
  return 'damage';
}

export function committedBattleEvents(before, after, actionId, start, duration = 0.55) {
  if (!before || !after || before.id !== after.id) return [];
  const old = before.log || [], next = after.log || [];
  // Also handle capped logs: find the retained old suffix in the new prefix.
  let retained = Math.min(old.length, next.length);
  while (retained > 0 && JSON.stringify(old.slice(-retained)) !== JSON.stringify(next.slice(0, retained))) retained--;
  const events = [];
  const beforeStacks = before.stacks || [];
  const afterStacks = after.stacks || [];
  const positions = new Map(beforeStacks.map(s => [s.id, [s.x, s.y]]));
  for (const [index, row] of next.slice(retained).entries()) {
    if (!['move', 'strike', 'retaliate', 'spell', 'cast'].includes(row.type)) continue;
    const sourceId = row.attackerId || row.casterId || row.stackId || (row.type === 'move' ? row.id : null);
    if (!sourceId) continue;
    const from = positions.get(sourceId) || null;
    const to = row.type === 'move' ? row.to : from;
    const targetId = row.defenderId || row.targetId || null;
    const isSpell = ['spell', 'cast'].includes(row.type);
    const spellId = isSpell ? (row.id || row.spellId || null) : null;
    const previousTarget = beforeStacks.find(s => s.id === targetId) || null;
    const nextTarget = afterStacks.find(s => s.id === targetId) || null;
    const caster = beforeStacks.find(s => s.id === sourceId) || afterStacks.find(s => s.id === sourceId) || null;
    const effectCategory = isSpell ? spellEffectCategory(spellId, previousTarget, nextTarget, caster) : 'damage';
    const selfTarget = Boolean(isSpell && sourceId && targetId && sourceId === targetId);
    const targetDied = effectCategory === 'damage' && stackBecameDead(previousTarget, nextTarget);
    const hpDelta = previousTarget && nextTarget ? stackPoolHp(nextTarget) - stackPoolHp(previousTarget) : 0;
    const countDelta = previousTarget && nextTarget ? (nextTarget.count ?? 0) - (previousTarget.count ?? 0) : 0;
    let affectedTargets = [];
    if (isSpell && spellId === 'fireball') {
      affectedTargets = afterStacks
        .map(s => {
          const prev = beforeStacks.find(b => b.id === s.id);
          if (!prev || prev.dead) return null;
          if (caster?.side && s.side && s.side === caster.side) return null;
          if (previousTarget && Number.isFinite(prev.x) && Number.isFinite(prev.y)
            && Number.isFinite(previousTarget.x) && Number.isFinite(previousTarget.y)
            && Math.max(Math.abs(prev.x - previousTarget.x), Math.abs(prev.y - previousTarget.y)) > 1) {
            return null;
          }
          const dHp = stackPoolHp(s) - stackPoolHp(prev);
          const died = stackBecameDead(prev, s);
          if (dHp < 0 || died) {
            return { id: s.id, effectCategory: 'damage', targetDied: died, hpDelta: dHp, countDelta: (s.count ?? 0) - (prev.count ?? 0) };
          }
          return null;
        })
        .filter(Boolean);
    }
    if (!affectedTargets.length && targetId) {
      affectedTargets = [{ id: targetId, effectCategory, targetDied, hpDelta, countDelta }];
    }
    events.push({
      eventId: `${after.id}:${actionId}:${index}`,
      actionId,
      sessionId: after.id,
      sourceId,
      targetId,
      kind: row.type,
      spellId,
      effectCategory,
      selfTarget,
      from,
      to,
      start: start + events.length * duration,
      duration,
      targetDied,
      hpDelta,
      countDelta,
      affectedTargets,
    });
    if (to) positions.set(sourceId, to);
  }
  return events;
}

export function motionFor(events, sessionId, actorId, time, reduced = false) {
  if (reduced || !Array.isArray(events)) return null;
  let event = null;
  for (let i = events.length - 1; i >= 0; i--) {
    const e = events[i];
    if (e.sessionId === sessionId && time >= e.start && time < e.start + e.duration
      && (e.sourceId === actorId || e.targetId === actorId || e.affectedTargets?.some(t => t.id === actorId))) {
      event = e;
      break;
    }
  }
  if (!event) return null;
  const progress = Math.max(0, Math.min(1, (time - event.start) / event.duration));
  if (['spell', 'cast'].includes(event.kind)) {
    const affected = event.affectedTargets?.find(t => t.id === actorId)
      || (event.targetId === actorId ? { id: actorId, effectCategory: event.effectCategory, targetDied: event.targetDied } : null);
    const effectCategory = affected?.effectCategory || event.effectCategory || 'damage';
    const died = effectCategory === 'damage' && Boolean(affected?.targetDied ?? event.targetDied);
    const targetClip = effectCategory === 'damage' ? (died ? 'death' : 'hit') : effectCategory;
    if (event.sourceId === actorId && (event.targetId === actorId || affected)) {
      return {
        ...event,
        progress,
        clip: 'cast',
        targetClip,
        effectCategory,
        targetDied: false,
        role: 'self-cast',
        selfTarget: true,
      };
    }
    if (event.sourceId === actorId) {
      return {
        ...event,
        progress,
        clip: 'cast',
        effectCategory,
        role: 'caster',
        selfTarget: false,
      };
    }
    return {
      ...event,
      progress,
      clip: targetClip,
      targetClip,
      effectCategory,
      targetDied: died,
      role: 'target',
      selfTarget: false,
    };
  }
  return {
    ...event,
    progress,
    clip: event.targetId === actorId ? (event.targetDied ? 'death' : 'hit') : event.kind === 'move' ? 'walk' : 'attack',
  };
}

export function activeCommittedFeedback(events, sessionId, time, reduced = false) {
  if (!Array.isArray(events) || !sessionId) return [];
  const sessionEvents = events.filter(e => e.sessionId === sessionId);
  if (!sessionEvents.length) return [];
  const lastActionId = sessionEvents[sessionEvents.length - 1].actionId;
  const latestActionEvents = lastActionId ? sessionEvents.filter(e => e.actionId === lastActionId) : sessionEvents;
  if (reduced) {
    return latestActionEvents.map(e => ({ ...e, progress: 0.5, reduced: true }));
  }
  return latestActionEvents
    .filter(e => time >= e.start && time < e.start + e.duration)
    .map(e => ({ ...e, progress: Math.max(0, Math.min(1, (time - e.start) / e.duration)), reduced: false }));
}

