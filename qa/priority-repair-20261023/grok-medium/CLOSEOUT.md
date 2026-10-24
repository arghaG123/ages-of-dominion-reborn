# Medium usability repair — 23 October 2026

**Executor:** Grok Medium usability executor  
**Scope:** D1–D7 from the 23 October bounded-repair guide  
**Disposition:** Reproduced Medium issues repaired and checked in the live local preview. D2 and D7 had no Medium defect to repair. This is not whole-game acceptance; Luna owns final combined verification.

## Scope and preservation

Changes are presentation and interaction feedback only. No campaign rules, economy, battle math, costs, save schema, progression, maps, assets, Android files, or APKs were changed. Gemini High and Luna Critical work was preserved. No Git publication, paid image work, APK build, or device test was performed.

The first preview opened at `http://127.0.0.1:4543/?audit` showed an existing campaign. I did not interact with it. I switched to `http://localhost:4543/?audit`, which showed “No campaign is stored on this device,” and used that empty origin for the natural-play checks. That origin now contains the disposable campaign used below; its reduced-motion setting was restored to its original off value, and its Defense session is paused.

## Changed files

- `src/client/main.js` — build time copy, skill-state copy, conditional damaged-save actions, Army inspector order, and tower inspection hit area.
- `src/client/kingdom-production.js` — presentation mirror for existing BUILD duration plus seconds formatting.
- `src/client/polish.css` — low-mana spell state styling, including the short-landscape heading rule.
- `src/client/screen-presentation.js` — shared skill state copy, current Defense wave summary, and conditional damaged-save recovery copy.
- `tests/kingdom-production.test.mjs` — BUILD duration parity and duration formatting regression.
- `tests/screen-presentation.test.mjs` — skill-state, Defense-wave, and recovery-copy regressions.

`main.js` and `polish.css` already contained Gemini/Luna work before this pass; the edits above were narrow additions to those files.

## Before and after evidence

| Item | Before | Repair and observed result |
|---|---|---|
| **D1 — Kingdom inspector** | Build confirmation showed price and level transition but omitted how long construction takes. | Confirmation now states `Construction time: 3 seconds.` at 825×375, 933×424, and 1280×720. A real Lumber Camp build cost 25 wood/15 stone; after completion the selected inspector showed `Lumber Camp · level 1`, `0.45 Wood per second`, and the real next upgrade price of 38 wood/23 stone. The upgrade preview showed level 1 → 2 and the same construction duration. No upgrade was committed. A focused regression compared the display helper with actual `BUILD` jobs for Lumber, Quarry, and Town Hall. |
| **D2 — Adventure routes** | No overlapping or incorrect route was reproduced. | Existing town shortcuts opened Quests → Story/Quests, Bag → Hero inventory, Camp → Travel and Sites, and Diplomacy → Story/Rival records. Each route reached its current feature; 48×48 shortcut targets and panel/dock separation were visible. No code change was needed and the approved Adventure maps were untouched. |
| **D3 — battle result and Defense** | At time-zero paused Defense, the HUD showed `0 / 5 waves` while the selected Defense detail showed `Wave 1 of 5`. The tower’s visible label did not activate inspection; the 21.6×21.6 px tower-body hit circle did. | HUD and detail now use the same current-wave wording (`Wave 1 of 5 · 400 gate HP`). Tower inspection targets now measure 64×64 CSS px. Their circular hit regions remain separated: approximately 6 px at 825×375, 16 px at 933×424, and 45 px at 1280×720. Tapping the visible Sling Post label opened `HP 144/150 · Range 2.9 · Damage 10`; tapping Tar Pit opened `HP 120/120 · Range 2.3 · Damage 3`. The paused Defense state survived reload. |
| **D3 — campaign and practice results** | Existing result renderer had actual settlement data, but a fresh natural campaign result had not been checked in this pass. | A real campaign Tactical Duel displayed Victory, 17 Clubmen with no losses, Slinger 7 survivors/1 lost, +150 gold, a recovered Offhand · Master, and +110 Hero XP. Settling and reloading retained the gold, item, 17 Clubmen, 7 Slingers, 5/10 Hero mana, and paused Defense. In an earlier isolated natural Skirmish, Practice showed its casualties and omitted campaign rewards. These are natural UI interactions in the disposable origin, not injected result fixtures. |
| **D4 — skills, spells, inventory, Forge** | A Wisdom-eligible spell could look ready despite insufficient current mana. Skills did not clearly distinguish a learned rank from an available offer. | The real post-battle Spellbook showed Mana 5/10: Magic Arrow and Bless (cost 5) were sufficient; Haste and Cure (cost 6) showed `LOW MP`; Wisdom-locked spells showed their actual required Wisdom. Selecting Haste stated `Unlocked · Not enough mana`. Skill cards now distinguish `No active offer`, `Available to learn`, and learned ranks without inventing a locked state. The real recovered Offhand · Master showed `def +2`, compared current Defense 3 → 5, and offered Equip/Compare. Forge comparison showed the same item and delta; normal Forge accurately explained `Armory required` and the actual next action. No Armory was invented or built. |
| **D5 — Army** | Recruit/Reinforce cost and capacity feedback followed the stat grid and fell below the compact inspector fold. | The action, actual cost, and blocking reason now precede the stat grid. At 825×375, 933×424, and 1280×720, the selected Clubman showed count, selection, 2/3 capacity, and its price/action before the stats. In real play, building a Barracks changed capacity from 2/2 to 2/3; Reinforce +5 charged 225 food/50 gold and changed Clubman ×12 → ×17. The next attempt was disabled with `Not enough resources.` Reload preserved ×17 and the 2/3 capacity. |
| **D6 — recovery, story, settings** | Damaged-save guidance promised backup restore even when no valid backup existed, and could say damaged bytes stayed stored when no raw bytes were available. | Recovery copy now lists restore/export only when `initial.backup` and raw damaged bytes are actually present; import and new campaign remain available. The helper regression covers no backup/no raw bytes, backup only, raw only, and both. Existing Story, quest, tutorial, and Settings copy did not show another false state in the scoped review. The actual Settings panel states the available controls and that English is the only language; reduced motion toggled on, persisted across reload, and was restored to off. |
| **D7 — shared presentation** | No remaining Medium inconsistency was reproduced in the inspected action icons, active tabs, selected cards, focus states, or secondary text. | Existing icon and focus treatments were retained. Only the local low-mana state styling was added; no shared stylesheet system or ornamental redesign was introduced. |

## Layout inspection

Live screenshots and accessibility state were reviewed at 825×375, 933×424, and 1280×720 for the changed Kingdom build confirmation, Army inspector, Spellbook, and Defense HUD/tower inspection. Prices, construction duration, current wave/core, low-mana feedback, and the selected Army action remained readable and in the intended panel. The screenshot images were reviewed in the browser during this pass; PNG captures were not written to this folder. Measured state and the before/after notes above are retained here.

## Verification

- `node --check src/client/main.js` — pass.
- `node --check src/client/screen-presentation.js` — pass.
- `node --test tests/kingdom-production.test.mjs tests/screen-presentation.test.mjs tests/defense-wave-presentation.test.mjs` — **29 passed, 0 failed**.
- Live preview console error log after reload — empty.
- No full test suite, APK build, install, or device test was run.

## Unresolved or intentionally unverified

- A natural skill-offer state was not reached; the four skill-copy branches were covered by the focused presentation test. The live campaign showed the truthful `No active offer` state.
- The damaged-save panel was not seeded with corrupted IndexedDB bytes in this pass. Its action-copy combinations were unit-tested; Luna should include the live damaged-save screen in combined verification if the current C1 browser fixtures do not already exercise it.
- Forge crafting affordability was not exercised because this campaign had no Armory. The existing `Armory required` state and the real Armory prerequisite were visible; no facility or cost was added.
- Story/quest/tutorial/settings wording outside the recovery cue had no reproduced Medium defect. Their existing behavior remains for Luna’s combined verification.

No Critical or High defect was confirmed within this Medium scope. The only additional D3 affordance issue reproduced was the small secondary tower-inspection target; it was repaired locally and checked for separation at all requested viewports. Whole-game, release, native/device, and owner acceptance remain outside this report.

## Combined recheck — 23 October 2026

**Disposition:** D1–D7 Medium implementation evidence was rechecked and the updated handoff is ready for Luna. No Critical or High defect was reproduced. This closes the Medium executor work described here; it does not claim combined or whole-game acceptance.

### Recheck changes and verification

- The combined suite exposed two stale spellbook source assertions in tests/visual-responsive-20261018.test.mjs. Updated them to assert the current LOW MP versus WIS state badge and the spell accessible name containing its description and current mana details. This is a test expectation correction; no runtime source changed during this combined recheck.
- node --test tests/visual-responsive-20261018.test.mjs — 39 passed, 0 failed.
- node --test tests/*.test.mjs — 303 passed, 0 failed after the assertion correction.
- Earlier focused Medium tests remain 29 passed, 0 failed; node --check passed for src/client/main.js and src/client/screen-presentation.js.
- Browser error log after the current natural campaign actions and reload was empty.
- Current source and report fingerprints are in source-hashes.json.

### Fresh natural-play recheck at the isolated origin

Used http://localhost:4544/?audit, which had no campaign before this pass. It now retains the disposable test campaign. The existing 127.0.0.1 user origin was not opened.

- **D1:** The current natural Lumber Camp preview showed 25 wood / 15 stone, level 0 → 1 and 3 seconds. After construction, the selected inspector showed Lumber Camp level 1, 0.45 Wood/sec and the real 38 wood / 23 stone upgrade. The upgrade preview showed level 1 → 2 and 3 seconds; it was canceled.
- **D2:** The prior live route checks remain: Quests → Story/Quests, Bag → Hero inventory, Camp → Travel and Sites, Diplomacy → Story/Rival records. No route overlap or wrong destination was reproduced; approved Adventure maps remain untouched.
- **D3:** A natural Campaign Tactical Duel ended in Victory after one legal Clubman strike: 17 Clubmen survived with no losses; 6 Slingers survived and 2 were lost; rewards were +150 gold, Bone Circlet · Fine, Winged Spurs and +110 Hero XP. Returning and reloading retained the rewards, losses and equipment. The earlier natural Practice check showed casualties and no campaign rewards. The paused Defense wave/core and direct tower-label inspections from the original pass remain current scoped evidence.
- **D4:** Built the existing Armory at P04 in the disposable campaign for its actual 120 wood / 120 stone / 80 gold and 3.1-second construction time. Before resources were sufficient, Crude crafting was disabled with the actual stone shortfall; higher qualities named their Armory-level requirements. After normal Quarry production, Craft · Crude became enabled at 80 wood / 60 stone / 70 gold. Confirming it created Flint Club · Crude in the inventory; comparison showed atk 3 → 4. Equipping it changed the weapon socket and survived reload. Bone Circlet · Fine comparison showed kno 1 → 2 and its equip also survived reload. The current Forge panel shows the real selected item, costs and quality gates.
- **D4 skill/spell state:** The live skill tree truthfully showed No active offer, rank 0 and 0 points. With the equipped circlet, the live Spellbook showed 10/20 mana, four actually eligible spells with their costs, and Wisdom requirements for locked spells. A natural skill-offer state was not reached.
- **D5:** Existing natural Army evidence remains: Barracks changed capacity from 2/2 to 2/3; Reinforce +5 charged 225 food / 50 gold and changed Clubmen ×12 → ×17; the next attempt was disabled for insufficient resources; reload retained the result.
- **D6:** The Medium recovery-copy tests cover no backup/no raw bytes, backup only, raw only, and both. Reduced motion was toggled, persisted across reload, then restored. I inspected Luna’s qa/priority-repair-20261023/luna-critical/c1-c2-c3-browser-evidence.json: its live damaged-save pass records Export damaged save and Restore valid backup, then a committed clean campaign. I did not recreate the damaged-save fixture in this recheck.
- **D7:** No further Medium issue appeared in the reviewed icon, active/focus, selection or secondary-text treatments.

### Current populated Forge layout

The live populated Forge was inspected at **825×375**, **933×424** and **1280×720**. At 825 and 933, the recipe panel scrolls and exposes the lower quality rows and selected-item summary; at 1280 the complete panel is visible. Prices, quality gates, equipped slot, carried item and selected item stayed legible. These screenshots were reviewed in CUA but no PNG files were persisted; current AX observations and before/after behavior are recorded in browser-evidence.json.

### Remaining combined-verification coverage

- No natural skill offer was available in the current campaign; the live state remained No active offer.
- The live damaged-save flow was not reseeded here; Luna’s current Critical browser evidence covers it.
- An active Tactical spell/effect animation was not played in this recheck. This remains a combined High visual coverage item for Luna; it is not a reproduced Medium defect.
- Practice’s no-reward result and Defense tower inspection were not replayed in this pass; their prior natural checks remain in the original closeout evidence.
- The isolated localhost:4544 origin retains the disposable campaign and is separate from the user origin.

No production game source, core rule, save, asset, map, APK or device state was changed in this combined recheck. No Git publication occurred.
### Files changed during this combined recheck

- tests/visual-responsive-20261018.test.mjs — corrected two stale spellbook source assertions at lines 165–166; the file also contains Gemini’s H3 responsive regression coverage.
- qa/priority-repair-20261023/grok-medium/CLOSEOUT.md — this recheck addendum.
- qa/priority-repair-20261023/grok-medium/browser-evidence.json — current natural-play and viewport evidence.
- qa/priority-repair-20261023/grok-medium/source-hashes.json — SHA256 and byte-size snapshot.

The earlier Medium implementation file list remains in the Changed files section above. No runtime production file changed during this combined recheck.