# M21 Spellbook context and cancellation review — 21 October 2026

**Result: Spellbook composition, cancellation, bounded core spell coverage, a natural Wisdom 3/Resurrection casualty-restoration journey, and one natural cast/effect/reload observation for all eight spells PASS. M21 is PARTIAL and the whole game remains INCOMPLETE.**

## Changes

- Hero > Spellbook now uses the selected campaign's registered Adventure map as a full-field scenic backdrop and places its panel in the lower-left, matching the approved composition. The bottom navigation moves to the lower-right; the six empty equipment sockets, generic equipment summary and tutorial action are hidden for this tab. Hero identity and the compact resource HUD remain visible.
- All eight spell cards remain in the panel with names, mana costs, Wisdom locks and accessible descriptions. Selecting a spell shows its source description, computed effect when available and mana without spending it.
- Tactical spell targeting now has a visible **Cancel spell selection** action. Cancel clears the intent and closes the target panel without issuing a battle command.

## Natural UI verification

`m21-spellbook-context-and-cancel-live-20261021.mjs` ran four isolated fresh campaigns at 825×375, 933×424, 1180×820 and 1280×720. Each journey opened the Spellbook over the selected Grasslands map, selected Magic Arrow, traveled through ordinary routes to a guard, opened a natural battle, canceled spell targeting, reloaded, then cast Magic Arrow and reloaded again. The final run passed at all four sizes with all eight cards visible, the panel confined to the lower-left half, and the footer clear on the lower-right.

- The correct map asset loaded in all four Spellbook views. The full-field scene and selected-spell feedback were visually reviewed; the panel stayed within the viewport.
- Cancel left mana, cast flag, round and battle-log length unchanged. Those values remained unchanged after reload.
- The next visible Magic Arrow cast spent exactly 5 mana and its spell event persisted after reload.
- Fresh run02 reached Wisdom 3 through visible offers, then naturally cast all eight spells and reloaded after every cast. Arrow, Bolt and Fireball changed enemy stacks; Bless, Haste and Slow applied their counters; Cure restored a naturally wounded stack; Resurrection restored a naturally lost creature. Every spell event, cost and observed effect persisted after reload.
- Earlier run01 stopped before Wisdom 3 at level 22 after 315 visible duels: mana was 0 and the naturally depleted campaign army was empty. It is retained as a failed progression run and is not counted as spell coverage.
- The run02 aggregate runner exited with a failed overall result because the final natural guard battle was lost after all eight casts. That loss does not erase the completed cast/effect/reload observations; the separate run09 Resurrection journey won and settled its natural guard battle.
- Zero page errors, console errors or failed network responses.
- Generic Hero equipment text and the tutorial toggle no longer add unrelated content to the Spellbook panel.
- Added a focused core regression covering all eight spell effects, mana costs, Wisdom gating, one-cast limit, wrong-side/dead targets, Fireball neighbour bounds, healing caps and effect-counter behavior.
- `node --test tests/*.test.mjs`: **235/235 PASS**, including the bounded save stress test.

## Remaining acceptance

The run02 all-spell journey reached Wisdom 3 at level 21 after 268 visible campaign duels and applied earned Knowledge points through the visible Hero controls. Six spells were cast in campaign Tactical Duels and each duel won through visible settlement. The natural Adventure guard then wounded the 12-member melee stack: Cure spent 6 mana (300 → 294) and restored 11/12 to 12/12; a later casualty reduced it to 11/12, and Resurrection spent 20 mana (294 → 274) and restored it to 12/12. Each cast and effect survived a reload. The guard battle later ended in defeat after repeated defend actions, so this is spell-cast evidence rather than a full successful campaign journey. Run09 separately proves a winning, settled natural Resurrection encounter. Evidence: [run02 report](m21-natural-all-spells-live-20261021-run02/report.json), [eight-cast contact sheet](m21-natural-all-spells-live-20261021-run02/natural-spell-cast-contact-sheet.jpg), [run02 runner](m21-natural-all-spells-live-20261021-run02.mjs), and [run09 winning natural Resurrection report](m21-natural-wisdom3-resurrection-live-20261021-run09/report.json).

All eight spell effects through natural progression and persistence are now **bounded PASS**. The separate [run02 leaf audit](m21-natural-all-spells-live-20261021-run02/spell-leaf-audit.json) validates the eight per-cast effects, exact mana costs, spell events and reload state against the full browser report; the aggregate runner's later defeat remains separately visible in that record. This review does not certify all 30 mock screens, all 18 journeys, all 32 age/mode scenes, independent desktop acceptance, the final APK, device checks or owner acceptance.

Evidence: `m21-spellbook-context-and-cancel-live-20261021/report.json` and its compact/desktop screenshots; [earned Wisdom 3 and Resurrection natural-run review](m21-earned-wisdom3-resurrection-natural-review-20261021.md). Adventure minimap evidence is in `adventure-minimap-map-art-live-20261021/report.json`.
