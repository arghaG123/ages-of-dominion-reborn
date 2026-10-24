# Independent combined verification — 23 October 2026

## Verdict

The three repair sets coexist in the current checkout. The independent integrated Node run passed **303 tests, 0 failures, 0 skipped/cancelled/todo** (`node --test tests/*.test.mjs`, 21,873.0118 ms). The run was performed in the parent portion of this same audit before the owner-requested chat transfer; it is independent of the executors' reported runs. No production source has been edited during this audit. The final source check matches **all 10/10** entries in the latest integrated executor fingerprint file. Current `main.js`: `12cea892e0e70a276ca93d2e9588717d61f4f03efc761ee036dacc23f286a385`, 295,264 bytes. See `source-snapshot.json` for 115 source/test/server entrypoint fingerprints.

**Remaining confirmed repair queue: no reproduced Critical defect; one active High presentation issue; two Medium clarity issues.** M03 Kingdom density/composition remains a separate **High / DEFERRED_OWNER** item. Whole-game acceptance remains **INCOMPLETE** because the active issues and the broader coverage limits below remain open.

This conclusion follows the current mock-adoption guide. Different chapter numbers, legal troop counts, actual prices, a strategic Adventure view, existing Market, and truthful Day-1 Walls0 are acceptable differences. They are not repair tasks. Do not restart the previous 30-exact-match tally.

## Confirmed remaining issues and exact repair scope

### H-01 — Tactical spell presentation still gives a positive spell a damage reaction

**High / CONFIRMED_FAIL — H3, M15/M21.** In the isolated restored starter campaign, start Skirmish, place Clubman and Slinger, cast Magic Arrow on Cave Bear in round 1, move the Clubman, Defend with the Slinger, then in round 2 cast **Bless on Clubman ×12**. Mana correctly changes 5 → 0. All six Clubman figures immediately report `data-plate-motion="hit"` and rotate 14 degrees, despite this being a friendly buff. The screenshot and DOM probe show a single unchanged PNG per figure, transformed as a whole. The cast has no distinct positive-effect presentation. This is observable misfeedback, not a request for a mock-specific projectile or a new combat mechanic.

Evidence: `practice-bless-immediate.png`, `committed-cast-probe.json`, `practice-arrow-immediate.png`, `practice-committed-move.png`. Scope is the sampled Stone formations, not a claim that every age/class was played. Movement is committed correctly: the live move probe contained six `walk` figures. That does not close the adopted articulated-motion requirement: these current troop consumers are `single-pose`, and creature figures are `plate`.

Cause: `src/client/committed-motion.js` drops the spell identity/effect category and gives every target a `hit` or `death` clip. When caster and target are the same stack, target precedence also suppresses `cast`. `src/client/main.js` `drawFigure` prefers `drawPlate` when a plate exists. `src/client/actor.js` `drawPlate` paints one image with whole-image transforms; `plateOffset` has no `cast` treatment. These are presentation paths; damage, buff duration, mana and settlement rules should remain unchanged.

Smallest repair: preserve spell identity/category in committed presentation events; distinguish buff/heal feedback from damage/death, preserve casting feedback for a self-target, and use the existing compatible actor/effect paths where they can meet the adopted motion requirement. Do not replace all art or change combat rules. Recheck Bless/Cure on self and another ally, Arrow on an enemy, committed movement/attack, lethal result timing, and reduced motion. Retain the legal-cell tray repair and current target geometry. Source tests alone cannot close the motion/pixel gate.

### D-01 — Spell instruction describes the wrong casting allowance

**Medium / CONFIRMED_FAIL — D4, M21.** Spell selection says **“A stack casts once this round.”** After the Clubman casts in round 1, the Slinger gets its turn in the same round and shows **“Spell. No cast”** even though 5 mana remains. The engine intentionally stores one `battle.castThisRound` flag and resets it in `nextRound`, so the guidance implies an allowance the player does not have.

Source: `src/client/tactical-ui.js:76`; engine authority `src/core/battle.js:534`, `:567`, `:587`. Repair the instruction and unavailable reason to describe one commander spell per round. Preserve the adopted rule. Stop after checking the second allied turn is explained and casting becomes available in the next round when mana permits.

### D-02 — Zero battle mana disappears from both visible and accessible hero status

**Medium / CONFIRMED_FAIL — D4, M21.** With 5 mana, the plaque displays `XP 0 · Mana 5`. Bless spends the final 5. At 0, the plaque displays only `XP 0`, and its accessible group also omits mana. The spell button is disabled as `Spell. No cast`, so the player loses the numeric value exactly when it explains an unavailable action.

Evidence: `zero-mana-omitted-825.png`, `zero-mana-dom.txt`, before/after Bless observations. Source: `src/client/main.js:1647` and `:1664`, both gated by `battle.mana > 0`. Render numeric zero in visible and accessible status; use a finite/present-value check. Check 0, 5 and the actual capacity without changing spell costs or save data.

### H-DEFERRED — Developed Stone Kingdom still lacks the approved dense composition

**High / DEFERRED_OWNER — H1/M03.** Preserve the owner deferral recorded in the current guide and `qa/game-completion-20261023/mock-scope-and-live-recheck-20261023.md`. The developed large-yard composition was previously confirmed; this audit did not reconstruct that mature state or claim a fresh mature-city screenshot. No producer repaired it, so it remains open rather than passed or demoted. Do not silently resume it, fake finished Day-1 buildings/walls, or count it as a new regression.

## Independently exercised integrated behavior

- **Fresh natural Mage campaign, localhost:4567:** started from no stored campaign; built P01 Lumber Camp through real cost and time confirmation (25 wood/15 stone, 3 seconds); saw level 1 production of 0.45 wood/sec and the real upgrade price. No resource grants or injected progression in this campaign.
- **Natural campaign combat and settlement:** four Tactical Duels exercised Bless, Magic Arrow, one legal strike, real casualties, +150 gold/+110 XP rewards and earned loot. The level-three Mage reached XP20, two attribute points and a real Luck/Tactics offer. Tactics confirmation consumed the offer once, learned rank1, preserved both attribute points and survived reload. `earned-level3-skill-offer-825.png`, `skill-learned-reload-825.png`. The earlier file `natural-skill-offer-825.png` is actually the level-two no-offer state; its filename is not evidence of an offer.
- **Tactical deployment:** all **11/11** highlighted cell centers self-hit at **825×375, 933×424, 1280×720**. Actual placements committed Clubman at 1,7 and Slinger at 2,7, enabling Start Battle. Cancel returned to War. `deployment-hit-probes.json`, `deployment-{825,933,1280}.png`, `deployment-placed-825.png`.
- **Defense:** Campaign Siege starts paused with Wave1 of5 and core400. Hero and actual Clubman deploy once; Resume runs, Pause returns to the same wave. Both tower inspection targets are approximately64×64 and center-hit themselves at all three sizes. `tower-hit-probes.json`, `defense-ready-825.png`, `defense-paused-{825,933,1280}.png`. This bounded sample is not five-wave victory or Endless completion.
- **Native storage fixture, 127.0.0.1:4567:** first confirmed all native stores and legacy campaign key empty. The QA-only page created revision0/gold150, committed revision1/gold151, rejected a stale writer without changing live bytes, preserved revision0 as backup, then deliberately damaged live bytes. The actual game detected damage, exposed the conditional recovery choices, exported the exact raw string `{independent-damaged-live`, restored the valid gold150 backup, saved and reloaded cleanly. A subsequent invalid import failed without replacing the campaign; Continue closed the error/panel and reloaded the intact campaign. See `recovery-fixture.html`, `native-recovery-fixture.txt`, `exported-damaged-save.txt`, recovery screenshots and text. This is explicitly fixture-based native-store evidence, not a natural damaged-player journey or quota/horizon proof.
- **Practice isolation on the restored fixture campaign:** real Skirmish controls, two rounds, Magic Arrow, Bless, movement, Defend and confirmed Retreat operated. Campaign gold150, XP0 and mana10/10 remained unchanged after practice spent battle mana to0 and lost a Slinger figure. Adventure then still showed 2 stacks/20 units. This supplements the executor's retained practice-result evidence; no new campaign reward was fabricated.
- **Adventure:** all four quick actions reached their existing functions. Quests scrolls the detail panel to saved quests, although the Chronicle/rival remains the surrounding screen; that is a valid route rather than a missing-feature defect. Bag opens inventory, Camp opens travel/rest/end day, Diplomacy focuses rival/story. Town route preview accurately showed cost8 versus5 available and blocked commitment. A separate legal east-step preview cost1; confirmation changed movement5→4, revealed Shrine, and reload retained4. `quests-shortcut-context-panel-825.png`, `adventure-825.png`, `travel-reload-4-moves.png`. This is a scoped route/fog/reload check; all crossings/worlds were not naturally traversed anew.

## Completed work retained, without repeating it

The final fingerprint comparison matches the integrated Medium handoff, including the Critical `game.css`, shared `main.js`/`polish.css`, presentation helpers and updated tests. The earlier High standalone `main.js`/`polish.css` hashes are historical before Medium additions; that difference alone is not lost work.

Retain the Critical backup/CAS/export/Continue fixes; Kingdom War navigation clearance; High compact deployment tray; Medium build-time/production copy, 64px tower picking, consistent wave wording, LOW MP/Wisdom distinction, skill offer states, Army action ordering and conditional recovery copy. Current direct checks above supplement their evidence.

Populated Forge/craft/equip/compare and Army recruitment were **not replayed independently in this fork**. The current-source executor handoff records natural Armory construction, Flint Club crafting/equip/reload (ATK3→4), Bone Circlet equip/reload (KNO1→2), and reinforcement ×12→×17 with matching payment. Its 10/10 fingerprint match makes that useful retained executor evidence; it does not turn it into an independent screenshot review. No PNGs were retained by that executor for the populated Forge recheck. Keep these rows as implemented/tested with that provenance, rather than redo them or claim full independent visual closure.

The Mage's empty-weapon wooden staff was examined as a possible misleading item. The body catalog explicitly identifies it as a class-focus prop rather than a worn weapon. No false equipped weapon/stat was reproduced; do not create a new repair merely from that silhouette. Likewise, Quests' surrounding Chronicle screen is not a broken destination: retained pixels show the scrolled quest controls.

## Coverage limits that remain VERIFY, not confirmed broken features

The combined reports overstate scope when their narrow starter samples are labelled unrestricted H1–H6/C1–C3 PASS. This audit does not certify every age, class/kit, six-slot worn attachment, every wall phase/site footprint, every Adventure crossing/map, all eighteen natural journeys, complete five-wave/Endless/Challenge outcomes, long-save quota/horizon, all accessibility/focus/inset cases or measured rendering performance. Those required assertions remain open unless a current applicable earlier record proves them. Do not send an executor to rebuild an unvisited screen merely because evidence is missing.

No new eight-age or M01–M30 closure count is asserted. The old exact-image tally mixes defects with permissible sample differences and should remain historical. The current priority guide governs this queue. Minor trim/lighting/prop preferences remain deferred.

Some inherited localhost campaign screenshots show distorted/soft text, while fresh captures in the new recovery tab are clearer. Capture quality is not established as an intrinsic rendering defect. No font/art replacement is prescribed from that alone. DOM geometry and actual screenshots were both inspected; neither is presented as a substitute for the other.

## Next action and preservation

Give the implementation AI only **H-01, D-01 and D-02**, with the checks above. Keep M03 deferred. Repair the causal presentation paths, verify those cases plus the shared compact screen, run affected tests and the integrated suite after the source changes, and retain the completed rows. No broad visual redesign or new mechanics are needed for these three items.

This verifier added only QA evidence/fixture scripts and handoff notes. No production repairs, new dependencies, paid images, asset-set replacement, APK build/install, device action, cleanup or Git publication occurred. The two disposable audit origins are distinct from the user's existing game origin. The natural Mage Defense was left paused; its campaign is preserved. Independent desktop acceptance, final snapshot APK, later device QA and owner review remain separate gates.
