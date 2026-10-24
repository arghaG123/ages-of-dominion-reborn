# Critical Functionality Verification & Bounded Repairs (C1, C2, C3) — 23 October 2026

- **Owner**: Luna (Critical-Functionality Executor)
- **Plan Reference**: `docs/plan/MOCK-ADOPTION-PRIORITIES-AND-BOUNDED-REPAIR-2026-10-23.md` (§2 Critical C1, C2, C3)
- **Isolated Verification Origin**: Ephemeral local HTTP server (`http://127.0.0.1:<ephemeral>`) with ephemeral temporary browser profile; never touched `localhost:4174` or user saves.
- **Machine-Readable Evidence**: `qa/priority-repair-20261023/luna-critical/c1-c2-c3-browser-evidence.json`
- **Automated Verification Script**: `qa/priority-repair-20261023/luna-critical/verify-c1-c2-c3.mjs`

---

## 1. Summary Verdict

| Priority Item | Scope | Status | Reproduced Defects Fixed |
|---|---|---|---|
| **C1** | Save Safety, Recovery, Conflict Handling, and Import/Export Protection | **PASS** | 6 bounded defects fixed in `src/core/storage-adapter.js` & `src/client/main.js` |
| **C2** | Campaign, Encounter, Settlement, and Transaction Continuity | **PASS** | 0 defects reproduced; all 9 live-UI & engine continuity/idempotence checks pass |
| **C3** | Critical Input Failures That Block or Mis-Execute Primary Actions | **PASS** | 1 bounded CSS hit-target occlusion fixed in `src/client/game.css` |

---

## 2. Changed-File List

### Production Files Modified (Bounded C1–C3 Scope)
- `src/core/storage-adapter.js`
- `src/client/main.js`
- `src/client/game.css`

### QA Artifacts Written (Strictly under `qa/priority-repair-20261023/luna-critical/`)
- `qa/priority-repair-20261023/luna-critical/verify-c1-c2-c3.mjs`
- `qa/priority-repair-20261023/luna-critical/c1-c2-c3-browser-evidence.json`
- `qa/priority-repair-20261023/luna-critical/c1-c2-c3-verification-and-repairs-20261023.md`

---

## 3. Fixed (Reproduced Defects & Bounded Repairs Applied)

### C1 — Save Safety, Recovery, Conflict Handling, and Import/Export Protection

1. **`preservePrevious` Overwriting Valid `backup` When `live` Was Damaged Due to Head/Payload Mismatch (`src/core/storage-adapter.js:35–48, 139–144, 211–215, 232–237, 290–295, 319–324`)**:
   - **Symptom**: When `campaigns.live` contained decodable JSON bytes whose `heads.live` metadata did not match (`!headsMatch(currentHead, headFor(state, raw, currentHead?.epoch))`), `loadLive(data)` classified the live save as `DAMAGED` (`Save head does not match campaign bytes`). However, `preservePrevious(store, raw, data)` only called `decode(raw, data)` without checking `headsMatch`, so a subsequent `replace()` or `restoreBackup()` overwrote `campaigns.backup` with the head-mismatched `previousLive` instead of archiving it under `damaged:<checksum>`. Additionally, the `useMemory` fallback branch of `loadLive(data)` omitted both `raw: live` on `DAMAGED` returns and the `headsMatch` validation present in the IndexedDB branch.
   - **Fix**: Updated `preservePrevious(store, raw, data, currentHead)` and all 4 call sites in `commit()` and `replace()` to verify `!currentHead || headsMatch(currentHead, headFor(state, raw, currentHead.epoch))`; when mismatched, `previousLive` is archived under `damaged:${checksum(raw)}` while keeping `campaigns.backup` intact. Added `raw: live` and `headsMatch` validation to the `useMemory` branch of `loadLive(data)`.

2. **Stale `initial.status === 'DAMAGED'` State After Backup Restore or Campaign Replacement (`src/client/main.js:279, 4769–4791`)**:
   - **Symptom**:
     - `Restore valid backup` in `home()` was shown whenever `if (!state && initial.backup)` held, and upon restoring the backup it set `state` and `view = 'kingdom'` without refreshing `initial`, `saveQueue.head`, `saveQueue.status`, or `lastSavedView`. Returning to `home` after restoring a backup still had `initial.status === 'DAMAGED'` and a stale `saveQueue.head` (`null`), causing subsequent saves to fail CAS or show damaged recovery controls.
     - Similarly, `replaceLive()` updated `state` and `saveQueue.head` without clearing `initial.status === 'DAMAGED'`.
   - **Fix**:
     - Gated `Restore valid backup` strictly on `if (!state && initial.status === 'DAMAGED' && initial.backup)`.
     - On backup restore completion, refreshed `initial = await idbAdapter.loadLive(data)`, synchronized `saveQueue.head = initial.head` and `saveQueue.status = { kind: 'committed', sequence: saveQueue.sequence, head: initial.head }`, set `lastSavedView = 'kingdom'`, and called `updateSaveFeedback()`.
     - Updated `replaceLive()` to refresh `initial` (`status: 'VALID'`, `head: saveQueue.head`, `state`, clearing `error` and `raw`).

3. **`Restore valid backup` Bypassing `replacementPending` Concurrency Guard (`src/client/main.js:4769–4791`)**:
   - **Symptom**: Rapid double-clicks on `Restore valid backup` invoked `idbAdapter.restoreBackup(data)` twice because `replacementPending` was neither checked nor set. Once the first call restored `live` to `VALID`, the second call threw `Error('Live save is valid')`, setting `saveFault = 'Live save is valid'` and displaying `'Save failed'` on the restored campaign.
   - **Fix**: Wrapped the `Restore valid backup` click handler in `home()` with `if (replacementPending) return; replacementPending = true; render();` and cleared `replacementPending = false` in `finally`.

4. **`Export damaged save` Relying Exclusively on Legacy `localStorage.getItem(SAVE_KEY)` (`src/client/main.js:4801`)**:
   - **Symptom**: `Export damaged save` in `home()` checked `if (!state && localStorage.getItem(SAVE_KEY))` instead of `initial.raw`, so a damaged save stored in IndexedDB (`campaigns.live`) could not be exported unless legacy `localStorage` also held a key.
   - **Fix**: Updated `home()` to resolve `const damagedRaw = initial.raw ?? localStorage.getItem(SAVE_KEY);` and gate `Export damaged save` on `if (!state && initial.status === 'DAMAGED' && damagedRaw != null)`.

5. **Rejected Import Leaving Sticky `saveFault` and Open Panel When Resuming Intact Campaign via `Continue` (`src/client/main.js:4745, 4817`)**:
   - **Symptom**: When an invalid import was rejected on `home` -> `Save/Load`, `import-file` set `saveFault = error.message` directly to display the error on the `Save/Load` panel. Clicking `Continue` to return to the intact campaign did not call `updateSaveFeedback()` or `setPanel(false)`, leaving `#status` stuck at `'Save failed'`, `#message` showing the import error, and `#panel` open over the resumed screen.
   - **Fix**: Updated both `Continue` handlers (`paintGate()` and `home()`) to call `updateSaveFeedback()` and `setPanel(false)` before navigating to `resumeDestination()`.

6. **Asynchronous `persist()` Rejection Not Updating `#status` / `#message` and Background Auto-Save Retrying Failed CAS (`src/client/main.js:261–266, 5114`)**:
   - **Symptom**: When `persist()` rejected asynchronously (e.g. `CAS head mismatch`), `.catch()` updated `saveFault` after `render()` had already completed, leaving `#status` and `#message` stale; furthermore, the 2000ms auto-save in `installLifecycle()` continued calling `persist()` even when `saveQueue.status.kind === 'failed'`, temporarily resetting `saveFault = 'saving'` right before the 1000ms `render()` tick and overwriting `'Save failed'`.
   - **Fix**: Updated `persist().catch(...)` to immediately set `$('status').textContent = 'Save failed'` and `if (view !== 'home') say(saveFault)`, and guarded the 2000ms auto-save tick in `installLifecycle()` with `saveQueue.status.kind !== 'failed'`.

### C3 — Critical Input Failures That Block or Mis-Execute Primary Actions

7. **Kingdom `#dock` Medallion Occluding `[data-choice="nav:war"]` on Compact Landscape (`825x375`, `933x424`, `933x425`) (`src/client/game.css:558–562, 1091`)**:
   - **Symptom**: On the Kingdom screen, `#nav` is positioned as a vertical left rail (`left: 12px`, `width: 58px`, `top: 52px` at `max-height: 500px`, spanning `y = 57..317px`). Meanwhile, `#dock` (`z-index: 7`, above `footer` `z-index: 6`) was positioned at `left: 10px; bottom: 68px;`, placing `#dock button` (`x: 10..58, y: 259..307` at `825x375`) directly on top of `[data-choice="nav:war"]` (`x: 17..65, y: 269..317`), causing center-point clicks on `nav:war` to hit `#dock button` (`hitSelf: false`).
   - **Fix**: Added `#app[data-view="kingdom"] #dock { left: auto; right: 14px; bottom: 14px; }` (and `left: auto; right: 10px; bottom: 12px;` under `@media(max-height:450px)`) in `src/client/game.css` so the Kingdom action medallion sits in the bottom-right corner clear of both the left `#nav` rail and the bottom-center `#panel`.

---

## 4. Verified Unchanged

- **C1 Core CAS, Migration, and Envelope Validation (`src/core/storage-adapter.js`, `src/core/save-envelope.js`)**:
  - Real `aod-reborn-v2` IndexedDB commit, revision/epoch tracking, SHA-like checksum verification, legacy `localStorage` migration (`migrateLegacyIfNeeded`), slot save/load (`slot:1`–`slot:3`), and export download mechanics were verified intact.
- **C2 Campaign, Encounter, Settlement, and Transaction Continuity (`src/core/engine.js`, `src/client/main.js`)**:
  - Verified without needing engine mutations across both live browser UI + reload (`liveUiTransactionAndReloadContinuity`) and deterministic engine transactions:
    - Action `id` idempotence (`idempotentTx`) and clean rejection of illegal/insufficient-resource builds without partial state mutation.
    - Kingdom plot construction (`BUILD` + `ADVANCE` completion) and resource deduction once (`buildCompleted`).
    - Adventure movement (`MOVE`) and one-time cache collection (`adventureMoveAndCacheOnce`) and site interaction (`INTERACT` once per cycle, `siteClaimOnce`).
    - Tactical encounter start, battle settlement (`SETTLE_BATTLE` once-only, `battleSettleOnce`).
    - Defense preparation, spell blast (`DEFENSE_CAST` mana spent once), and settlement (`SETTLE_DEFENSE` once-only, `defenseBlastAndSettleOnce`).
    - Forge item crafting (`FORGE`), equip, and unequip (`UNEQUIP`) stat and resource accounting (`forgeEquipAndUnequip`).
    - Quest claim once-only (`CLAIM_QUEST`) and Age advancement (`AGE_UP`) continuity (`questClaimOnceAndAgeUp`).
- **C3 Coordinate Picking, Drag Cancellation, and Modal Inert Protection (`src/client/main.js`)**:
  - Inverse scene coordinate picking (`clientToSource` / `pickSiteAtClient` for `townhall` and `P01`), pointer drag-cancellation (`>8px` movement suppresses synthetic click activation), and modal background blocking (`#build-confirm` and `#retreat` setting `stage.inert`, `header.inert`, and `footer.inert`, plus `rebornHandleBack()` dismissal) were verified intact across `825x375`, `933x424`, `933x425`, `1280x720`, and `1376x768`.

---

## 5. Unresolved

- **None** within C1, C2, or C3 scope. All 6 C1 checks, 9 C2 checks, 5 C3 viewport matrices (`825x375`, `933x424`, `933x425`, `1280x720`, `1376x768`), C3 modal inert checks, and all 299 Node unit tests pass (`overallPass: true`).

---

## 6. Handoff Items (for Gemini and Grok)

1. **For Gemini (H1–H4 High-Priority Mock Adoption & Layout/Visual Polish)**:
   - Note that `#app[data-view="kingdom"] #dock` in `src/client/game.css` is now anchored at `left: auto; right: 14px; bottom: 14px;` (and `right: 10px; bottom: 12px;` at `@media(max-height:450px)`) to prevent `#dock button` from overlapping `[data-choice="nav:war"]` in the left vertical `#nav` rail on compact landscape (`825x375`, `933x424`, `933x425`). Preserve this non-overlapping placement when adjusting H1/H2 HUD or Kingdom dock styles.
   - `Continue` handlers in `src/client/main.js` (`paintGate` and `home`) now invoke `updateSaveFeedback()` and `setPanel(false)` before transitioning to `resumeDestination()`. Preserve this behavior if modifying M01 gate or home menu actions.
2. **For Grok (M1–M3 Medium-Priority Polish & Final Consolidation)**:
   - Machine-readable browser verification evidence is saved at `qa/priority-repair-20261023/luna-critical/c1-c2-c3-browser-evidence.json` and can be re-executed anytime via `node qa/priority-repair-20261023/luna-critical/verify-c1-c2-c3.mjs` (runs isolated on an ephemeral port and temporary browser profile without touching `localhost:4174`).
