# Priority Repair Closeout: H-01, D-01, D-02 (2026-10-24)

## 1. Scope & Authority
- **Authoritative Spec**: `docs/plan/MOCK-ADOPTION-PRIORITIES-AND-BOUNDED-REPAIR-2026-10-23.md`
- **Combined Independent Audit**: `qa/priority-repair-20261023/independent-combined/REPORT.md`
- **Active Repair Items**:
  - **H-01 (High)**: Tactical spell presentation, immediate post-command motion, positive spell reaction, self-cast preservation, and distinct category feedback (`PASS` on positive spell reaction, self-cast preservation, immediate post-command motion, and distinct category feedback; `PARTIAL_ASSET_LIMITATION` on whole-image troop/creature plate articulation).
  - **D-01 (Medium)**: Tactical spell allowance guidance (`Your hero casts once per battle round.`) and explicit disabled-state reasons (`round-used`, `insufficient-mana`, `no-known-spell`, `no-target`) visible without hover (`PASS`).
  - **D-02 (Medium)**: Zero battle mana (`Mana 0`) visible and accessible in the Tactical hero plaque (`PASS`).
- **Preserved Owner Deferral**:
  - **M03 (High / `DEFERRED_OWNER`)**: Developed Kingdom density/composition preserved untouched.

---

## 2. Root Causes & Substance of Changes

### H-01 — Tactical Spell Presentation & Immediate Post-Command Motion
1. **Cross-Command Event Queue Delay (`src/client/main.js`)**:
   - **Root Cause**: In `act()`, newly generated `committedBattleEvents` were previously offset by `const end = Math.max(motionTime, ...battleEvents.map(event => event.start + event.duration))` (`start + end - motionTime`). When a player cast a spell or moved immediately after a prior turn whose 0.55s–0.65s animation had not finished expiring, the newly committed command's events were scheduled in the future (`start > motionTime`), so immediate post-command DOM sampling observed the previous command's `walk` animation instead of the newly committed `cast`/`buff`/`hit` animation.
   - **Fix**: Replaced cross-command queueing with immediate replacement (`if (events.length) battleEvents = events;`) at `motionTime`, while `committedBattleEvents` continues to sequence multi-step events within a single command (`start + events.length * duration`). Also scoped `activeCommittedFeedback` in `src/client/committed-motion.js` to the latest `actionId` so prior commands' spell badges do not linger across subsequent player commands.
2. **Board Cell & Target Pad Interception by Unit Sprites (`src/client/main.js`)**:
   - **Root Cause**: In `drawFigure()`, `figGroup` (`g[data-stack-id]`) did not set `pointer-events: none`, allowing the 6 unit `<image>` plates to overlap adjacent board cells (`polygon[data-cell]`) and intercept `document.elementFromPoint(cx, cy)`.
   - **Fix**: Added `'pointer-events': 'none'` to `figGroup` so board cell polygons (`[data-cell]`) and target pads (`rect[data-target]`) receive all pointer clicks cleanly.
3. **Spell Category & Self-Cast Motion Semantics (`src/client/committed-motion.js`, `src/client/actor.js`, `src/client/anatomy.js`, `src/client/main.js`)**:
   - `committedBattleEvents()` classifies spells via `spellEffectCategory(spellId)` into `damage` (`arrow`, `bolt`, `fireball`), `buff` (`bless`, `haste`), `heal` (`cure`, `resurrect`), and `debuff` (`slow`), recording `selfTarget` (`casterId === targetId`) and `affectedTargets` (including AoE `fireball` targets).
   - `motionFor()` iterates backward so the latest active event wins, returning `clip: 'cast'` with `targetClip: 'buff' | 'heal'` on self-casts (`selfTarget: true`), `clip: 'buff' | 'heal' | 'debuff'` on non-self spell targets, and `clip: 'hit' | 'death'` only for `damage` spells and physical attacks.
   - `clipAngles()` and `plateOffset()` in `src/client/actor.js` and `paintedPose()` in `src/client/anatomy.js` implement upright/uplifted `cast`, `buff`, `heal`, and `debuff` poses (`rotate(-2)` / `rotate(-1.5)` / `rotate(0)` / `rotate(4)`), preventing friendly buffs and heals from ever playing `hit` (`rotate(14)`) or `death` (`rotate(70)`) recoil.
   - `drawTacticalCommittedFeedback()` in `src/client/main.js` renders distinct SVG feedback motifs per spell category (`damage-impact`, `buff-crest`, `heal-restoration`, `resurrect-crown`, `slow-shackle`) and closes `#panel` (`setPanel(false)`) when a `spellcast:...` choice is clicked.
4. **Honest Asset Limitation Disclosure (`PARTIAL_ASSET_LIMITATION`)**:
   - Current runtime troop and creature sprites (`assets/runtime-code-20261007/troops/*.png`, `assets/derivatives/image-vertex-repair-20261009/actors/troops/*.png`, `assets/derivatives/image-complete-20261011/actors/plates/*.png`) are `single-pose`/`plate` whole-image PNGs rendered via `drawPlate` with whole-image `translate(...) rotate(...)` transforms rather than multi-part jointed rig anatomy. While hero/jointed-role rigs support full limb articulation and troop/creature plates now accurately reflect `cast`, `buff`, `heal`, `debuff`, `walk`, `attack`, `hit`, and `death` without false damage recoil, full multi-part troop limb articulation remains `PARTIAL_ASSET_LIMITATION` unless new multi-part troop rig assets are authored.

### D-01 — Casting Allowance Guidance & Explicit Unavailable Reasons
- Updated `intentSentence('spell', ...)` in `src/client/tactical-ui.js` from `"A stack casts once this round."` to `"Choose one listed cast. Your hero casts once per battle round."`, matching `battle.castThisRound` reset by `nextRound` in `src/core/battle.js`.
- Added `spellAvailability()` and `battleSpellAvailability()` in `src/client/tactical-ui.js` to distinguish `available`, `round-used` (`Round cast used (1/round)`), `insufficient-mana` (`Insufficient mana (current/min)`), `no-known-spell` (`No spells learned`), and `no-target` (`No valid spell targets`), wired into `modeRows()`, `primaryModeRows()`, the Tactical status bar (`[data-spell-allowance]`), the Spellbook guidance line (`[data-spell-guidance]`), and the dock Spell button (`data-spell-reason`, `title`, `aria-label`).

### D-02 — Zero Battle Mana Visibility
- Added `tacticalHeroPlaqueCopy()` in `src/client/tactical-ui.js` and wired `paintTacticalHeroPlaque()` in `src/client/main.js` to check `Number.isFinite(mana)` instead of `battle.mana > 0`.
- When battle mana reaches `0`, `.tactical-hero-plaque` displays `XP <n> · Mana 0` and includes `Mana 0` in its `aria-label`, maintaining an identical `70px` plaque height (`plaqueHeightWithMana: 70`, `plaqueHeightZeroMana: 70`) and `0.9094` useful world ratio at `825×375`.

---

## 3. Changed File Fingerprints (SHA256 & Bytes)

| File | Bytes | SHA256 |
|---|---:|---|
| `src/client/committed-motion.js` | 8,196 | `461db5a6de89c27300bc0810c28a0eb0f8ae987424ba0b80ab771c0d5288b987` |
| `src/client/tactical-ui.js` | 12,746 | `6c0afd646a7e00ba6b3f015edb3cd9f40eb83d42efed99d1b8cb075dd4ac7a5b` |
| `src/client/actor.js` | 27,942 | `73ca55e44dd8ab233ba36315815c3f39342590c7095917b4a889c708c9f85068` |
| `src/client/anatomy.js` | 6,385 | `c47edf06b3f38b9dfbc97b8070ef84c9d98ed79353a0f2c2af73cdf6e66eb78d` |
| `src/client/main.js` | 305,885 | `461fca7396f582ac4834b72b5d684d13e8c6567fb95c0fded7e70197f3678987` |
| `tests/committed-motion.test.mjs` | 8,719 | `d4c4ed042d9a8cfb7e12ebefa3ac508d5cf1333220752bf895d1d3a9f00c59e1` |
| `tests/tactical-ui-20261005.test.mjs` | 7,921 | `0bffe5f60522cb847922861c560564d3952ef8e31f13f3028dc9ae628c57a9e3` |
| `tests/tactical-action-bar-20261022.test.mjs` | 2,067 | `89fcec369ff48141cefc0852e73f379d950a621bf5d4eff427ab17f9bf394e27` |

---

## 4. Verification Evidence (`qa/priority-repair-20261023/remaining-high-medium/`)
- `focused-tests.log`: 17/17 focused unit tests passing (`tests/committed-motion.test.mjs`, `tests/tactical-ui-20261005.test.mjs`, `tests/tactical-action-bar-20261022.test.mjs`).
- `full-suite.log` / `full-test-suite.log`: 311/311 repository unit tests passing (`node --test tests/*.test.mjs`).
- `verify-live.mjs` & `verification-summary.json`: Live headless Chromium verification in isolated ephemeral contexts at `825×375`, `933×424`, and `1280×720`.
- `committed-cast-probe.json`: Live DOM figure probe immediately after Round 2 self-cast `Bless` on `Clubman ×12` (`motion: "cast"`, `targetClip: "buff"`, `spellCategory: "buff"`, `selfTarget: true`, `rotate(-0.47587934159383427)`).
- `deployment-hit-probes.json` & `tower-hit-probes.json`: 11/11 Tactical deployment legal cells and 4/4 Defense tower pads (~64×64px) verified self-hitting at `825×375`, `933×424`, and `1280×720`.
- Screenshots:
  - `practice-arrow-immediate.png`
  - `practice-committed-move.png`
  - `practice-bless-immediate.png`
  - `zero-mana-visible-825.png`
  - `tactical-825x375-spell-damage-and-round-used.png`
  - `tactical-825x375-spell-buff-self.png`
  - `tactical-825x375-spell-heal-resurrect.png`
  - `tactical-825x375-spell-debuff-slow.png`
  - `tactical-825x375-zero-mana-and-guidance.png`
  - `tactical-933x424-spell-and-zero-mana.png`
  - `tactical-1280x720-spell-and-zero-mana.png`
