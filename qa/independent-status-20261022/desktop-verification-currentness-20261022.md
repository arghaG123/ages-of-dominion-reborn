# Desktop verification currentness audit — 22 October 2026

**Status: INCOMPLETE.** The current verifier-only task requires independent live-browser gameplay, screen review, and comparisons against the approved mock set. The initial browser-policy blocker was cleared after the user approved the existing isolated in-app route `http://localhost:4174/?audit`; scoped visual review has resumed only there. All 30 mock IDs have explicit current review records, but several are unmatched or partial. Remaining mock acceptance, J01–J18 coverage, repairs, compact-size review, desktop acceptance, and release gates remain open. No production source was edited.

## Initial browser-policy block — superseded by owner approval

- The in-app browser inventory showed tab 1 at `http://127.0.0.1:4174/` with the title “This site can't be reached.” No listener was present on port 4174.
- Started the repository's local preview with `npm run dev -- --host 127.0.0.1 --port 4174`; it reported that it was serving `http://127.0.0.1:4174`.
- The browser tool then denied observing that local page under its URL policy and instructed against reaching it through another browser surface, Playwright, CDP, or other workaround. No alternate access path was attempted.
- Stopped the preview process. Port 4174 is no longer serving. No page state, gameplay, or new screenshot was collected in this attempt.

The original route-access block is historical and no longer prevents the scoped live review. The complete desktop verification gate remains open.

## Evidence currentness

The saved [Adventure v4 correction report](../game-completion-20261022/visual-review/adventure-map-source-reconciliation-20261022/adventure-map-source-correction-and-verification-v4-20261022.md) and [per-world v1–v4 matrix](../game-completion-20261022/visual-review/adventure-map-source-reconciliation-20261022/per-world-map-source-geometry-v4-20261022.json) are the current evidence for the map-source correction: 12 generated production maps, matching v4 geometry, 240 deterministic layouts, migration checks, Astral Peaks `[13,5]`, and three open-inspector viewport measurements. The stored 825×375 and 1280×720 Adventure captures were visually reopened in this audit; they show the generated landscape contained in its map pane. This is a bounded Adventure view, not a fresh current-browser run or a full mock-fidelity acceptance.

The broad [independent live desktop review](../game-completion-20261022/visual-review/independent-live-desktop-review-20261022-run01.md) and [independent-status verification](VERIFICATION.md) predate the v4 map correction. Their source hash snapshot differs from the current files:

| File | Earlier audit hash | Current hash |
|---|---|---|
| `src/client/main.js` | `03af0e241d2a1fc9c15fae8e8e0cc14981b6c5626ceff55cd79c0072d360b02a` | `A4E205C0D6275FE43C8A9753F56230FAF2CBCDAA38541DD95D0FDD0D76A63462` |
| `src/client/game.css` | `f383dac6a6cacc3cab00de7d5ded7624e2b914489d5fe36ac6c02026f6ef46f0` | `9921d5e885749d6278cd62db69200e242d17080e7f69429c5ae2863284534ad0` |
| `src/client/adventure-map-source.js` | `489938c4dee18794cd07b77d886a143e077e29fdc7663db0d4ed1b66a9ed4354` | `0d5e6b5c98854d48889e83fd30d0e85b6daf14fbaa2fe6aba873cee1215c5c19` |
| `src/core/campaign.js` | `ffe8c99d1f7a61b5bfda74074edd3e84055f7b344537b781c3ac01f685bbcbdc` | `d1c45e1d670ffcfb67b46f17bb8ccb4ccdab51484a202ebc671c3b23b593ed9d` |
| `src/core/navigation.js` | `71da3d369a343a2538c85c7b9a3e70c2c4b3f08d6299d1ec73421616deb2fa7b` | `03d7742f11447e20ae76484bd55505380635f2672a002832982da0ab468bf51a` |
| `src/data/adventure-worlds.json` | `6b5cef016aa4880478655a04d48531a93d9735ad3aafe77e0ee9dc42757d8ec8` | `efd4ff11d5cfee4824134a1eb1224c791d58be75aa508c8124af15143ac1646d` |

The older all-world one-move report at `adventure-all-worlds-natural-live-20261022-run01/report.json` is dated 21 October and records the supplied example pictures as runtime images. Its `passed: true` result is bounded evidence for its old one-move/save/reload journey; its map images and screenshots do not represent the current generated-map runtime and must not be used for current map visual acceptance.

The prior broad review's compact-cropping, Forge, duplicate Siege action, Story fit, and Siege-victory observations are not promoted here as current defects: relevant UI sources changed after that capture, and the browser attempt above produced no current screenshot. Recheck them in a fresh matched browser session. The v4 map report and older crop measurements also use different layout observations; current compact map framing needs the approved live review conditions to reconcile them.

## Work still required

- Continue on the owner-approved in-app route and close the remaining M01–M30 mock comparisons with matched states, required repairs and retained evidence; verify J01–J18 live journeys at current source hashes.
- Recheck all three landscape sizes, map edges, open inspectors, actor grounding, the map source/geometry binding, Story fit, Forge states, Defense setup and results, tactical modes, class/gear/motion presentation, and save/recovery flows.
- Keep final package verification, phone/device QA, and owner acceptance as later separate gates. No APK was built and no device was used in this audit.

At the time of this initial audit, the overall game and desktop verification were **INCOMPLETE**, and the browser-policy block prevented current live evidence. The user later approved the existing localhost route; that block is superseded below and is no longer the current constraint.

## Continuation recheck

At that continuation recheck, the in-app browser still contained only its connection-error page for `127.0.0.1:4174`, port 4174 was stopped, and the active goal remained **INCOMPLETE**. That pre-approval state is historical. The user subsequently approved the existing `localhost` route recorded below.


## Owner-approved localhost continuation — 22 October 2026

After the earlier browser-policy audit, the user directly approved the existing isolated in-app localhost route. Current live review has proceeded at http://localhost:4174/?audit through the approved tab; no alternate browser, automation surface, or port was used. All 30 mock IDs have explicit current visual-review records. M02/M03/M06/M15 are visual FAIL; M04/M05/M07–M10, M12–M14, M18, and M27 are OPEN for unmatched age/state; M01/M11/M16/M17/M19–M26/M28–M30 are PARTIAL. The failed two-wave natural Endless attempt remains separate behavior evidence. Mock record coverage does not complete M01–M30 acceptance, J01–J18, repairs, independent desktop review, package, device, or owner gates.

### M14–M16 tactical review follow-up — 22 October 2026

At this checkpoint the run01 dossier had records for 24 of 30 mock IDs: M01–M03, M06, M11–M16, and M17–M30. M15 is a direct visual FAIL; M14 is OPEN because the practice battle did not expose deployment; M16 is PARTIAL because only the shared practice-result presentation was reached. The approved CUA tab started a Skirmish, captured Round 1 and the result, then returned to the Medieval day-4 campaign; slot 1 was untouched. Live screenshots were observed but not retained. No game source, tests, package, device, provider, Git, or cleanup action occurred.

Current hashes recorded for the tactical review: main.js A4E205C0D6275FE43C8A9753F56230FAF2CBCDAA38541DD95D0FDD0D76A63462; game.css 9921D5E885749D6278CD62DB69200E242D17080E7F69429C5AE2863284534AD0; campaign.js D1C45E1D670FFCFB67B46F17BB8CCB4CCDAB51484A202EBC671C3B23B593ED9D; battle.js E407169CC87AB3825DB58541F2EEFA4AA3A8F12196107EE50D7FCBE0CA7C15E3. This source snapshot does not close mock, journey, compact-size, desktop, package, device, or owner gates.

Records: qa/game-completion-20261022/mock-live-review-run01/m14-tactical-deployment-skirmish-state-unmatched-live-review-20261022.json, m15-tactical-action-skirmish-live-review-20261022.json, and m16-battle-result-practice-result-partial-live-review-20261022.json.

### M18 Endless active-wave mock review — 22 October 2026

The natural Medieval day-4 campaign reached Endless preparation only. The mock depicts active Endless wave 14/20 at 84% gate health; the current view has no active session, wave, gate/core health, or deployed forces. No Start Endless, purchase, retrofit, or deployment action occurred. A separate natural Stone-age two-clear defeat is not visual evidence. M18 remains OPEN. The screenshot was observed but not retained.

### M04–M10 later-age Kingdom state checks — 22 October 2026

The approved route showed the natural Medieval day-4 Kingdom at 1280 × 720. The six targets are other ages and specific selected-building states: Bronze/Clay Workshop, Iron/Market, Gunpowder/Artillery Foundry, Industrial/Iron Foundry, Modern/Residential Tower, and Future/Advanced Research Lab. No age advancement or building selection occurred. All six records are OPEN, with screenshots observed but not retained. Reference hashes were checked against the six mock files. The complete run01 set now has evidence rows for M01–M30; this is coverage, not acceptance. Current source hashes for the observed Kingdom renderer are main.js A4E205C0D6275FE43C8A9753F56230FAF2CBCDAA38541DD95D0FDD0D76A63462 and game.css 9921D5E885749D6278CD62DB69200E242D17080E7F69429C5AE2863284534AD0.

## Historical ledger and mock-coverage recheck — 22 October 2026

- `qa/mock-led-executor-20261016/completion-contract.json` is evaluated at `2026-10-17T12:17:03Z` and reports overall `INCOMPLETE`; its self-reported summary says 277/277 leaves passed and zero failed, blocked, or unverified. That summary is dated and has not been independently refreshed against current source and retained evidence. The owner-current independent verification and this live review still find open requirements, including direct visual failures M02, M03, and M06; treat the old leaf PASS labels as historical claims, not current completion proof.
- `qa/mock-led-executor-20261016/journeys.json` is evaluated at `2026-10-17T12:16:10Z` and claims 18/18 journeys passed, with 13 classified natural and five `natural_and_simulation`. These dated suite references do not provide current natural-play captures or prove current source behavior. Reverify J01–J18 against the current implementation and retain each required trace.
- At the earlier snapshot, the run01 directory had records for 21 mock IDs. The M14–M16 follow-up expanded it to 24, then M04/M05/M07–M10 brought record coverage to all 30 mock IDs. M18's record is a natural Endless defeat after two non-leaked clears; it is not a mock-fidelity pass. M02/M03/M06/M15 are visual FAIL; M04/M05/M07–M10/M12–M14/M27 remain OPEN; M01/M11/M16/M17/M19–M26/M28–M30 remain PARTIAL. M18's ten-wave natural requirement failed and its age-matched visual comparison remains open.
- The newly added M11–M13 and M17 evidence records parse and their mock SHA-256 values match; their live screenshots were observed through CUA but not retained. The current mock review is coverage evidence, not completion acceptance.

### Owner-approved localhost M17 Campaign Siege preparation review — 22 October 2026

At exact 1280 × 720, the natural slot-2 Medieval Campaign Siege preparation page shows a five-wave mode, two tower markers, and retrofit options. M17 shows a river-gorge castle scene with deployed hero/army, owned-roster tray, and 0/15 preparation HUD. Scene and hierarchy differ; M17 remains PARTIAL. No battle, tower purchase, retrofit, or deployment action occurred. Record: `qa/game-completion-20261022/mock-live-review-run01/m17-defense-preparation-natural-medieval-live-review-20261022.json`. Screenshot observed but not retained.

### Owner-approved localhost M11 Adventure overview review — 22 October 2026

At exact 1280 × 720, the natural Medieval Adventure screen shares M11's full landscape, minimap, hero marker, and location labels. The focal settlement, labeled resources, hero HP/XP panel, and four-button Adventure action bar differ. M11 remains PARTIAL. No movement or location action was invoked. Record: `qa/game-completion-20261022/mock-live-review-run01/m11-adventure-overview-natural-medieval-live-review-20261022.json`. Screenshot observed but not retained.

### Owner-approved localhost M12 unmatched crossing state — 22 October 2026

The natural Medieval Travel and sites panel lists one-step directions and guidance for three marked crossings, but no crossing is selected. M12's specific bridge scene and Cross Bridge action are therefore unmatched. M12 remains OPEN. No movement or tutorial skip was invoked. Record: `qa/game-completion-20261022/mock-live-review-run01/m12-adventure-crossing-natural-map-live-review-20261022.json`.

### Owner-approved localhost M30 icon review — 22 October 2026

The approved route was used for a read-only exact 1280 × 720 comparison of the natural Medieval slot-2 Story and Army views against M30. Reference hash and the partial result are recorded in qa/game-completion-20261022/mock-live-review-run01/m30-icon-material-board-live-review-20261022.json; the live screenshots were observed in CUA but not retained. This extends currentness only to those two screens and does not close the M01–M30 icon inventory, other mock screens, compact sizes, independent desktop, package, device or owner gates.

### Owner-approved localhost M20–M21 continuation — 22 October 2026

At exact 1280 × 720, current Hero Skills and Spellbook surfaces were observed in the approved in-app route. The nine-skill tree and eight spell families are present; current campaign state does not match the armory and active-battle mock compositions. Records: qa/game-completion-20261022/mock-live-review-run01/m20-skills-natural-medieval-live-review-20261022.json and m21-spellbook-natural-medieval-live-review-20261022.json. Live screenshots were not retained. This does not close either mock, skill/spell journeys, compact sizes or owner acceptance.

### Owner-approved localhost M22 Forge continuation — 22 October 2026

The approved route showed the current Medieval Forge at 1280 × 720. Its sword/anvil/fire composition strongly matches M22, while the catalog controls remain incomplete. Evidence is in qa/game-completion-20261022/mock-live-review-run01/m22-forge-natural-medieval-live-review-20261022.json. The live screenshot was observed but not retained. This does not close M22, M23 inventory, compact sizes or owner acceptance.

### Owner-approved localhost M23 inventory comparison — 22 October 2026

At exact 1280 × 720, the current Forge comparison panel was opened by selecting the carried Flint Club. It exposes one carried item, six empty gear slots, an atk +1 comparison, and an Equip action left untouched. The complete M23 inventory grid was not reached. Evidence is in qa/game-completion-20261022/mock-live-review-run01/m23-inventory-natural-medieval-live-review-20261022.json. Screenshot observed but not retained.

### Owner-approved localhost M27 tutorial current-state check — 22 October 2026

The natural Medieval Kingdom screen was reviewed at exact 1280 × 720. The current campaign has no tutorial callout, step text, Next action or progress marker; M27’s Stone-age Build Farm step remains unmatched. No construction, skip or save action occurred. Record: qa/game-completion-20261022/mock-live-review-run01/m27-tutorial-natural-medieval-live-review-20261022.json. Screenshot observed but not retained.

### Owner-approved localhost M19 Hero room review — 22 October 2026

The approved route showed the natural Medieval Hero room at exact 1280 × 720. It has six accessible empty slots and one carried Flint Club; the avatar appears armored despite empty equipment state. The M19 reference selected-gear comparison is absent. Evidence: qa/game-completion-20261022/mock-live-review-run01/m19-hero-equipment-natural-medieval-live-review-20261022.json. The live screenshot was observed but not retained.
