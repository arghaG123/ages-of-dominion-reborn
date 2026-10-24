# M21 earned Wisdom 3 and Resurrection natural-run review — 21 October 2026

**Result: Natural Wisdom 3 progression, Resurrection access, casualty restoration, and reload persistence PASS. A second fresh visible campaign also cast all eight spells, verified each effect, and verified reload persistence. M21 remains PARTIAL and the whole game remains INCOMPLETE.**

## Earned progression

Run09 used a fresh isolated browser with no seeded save, injected XP, or injected resources. The player selected Mage and Jade Karst through visible campaign choices, reached the shrine by confirmed Adventure routes, and chose only visible offers. The shrine's offer did not contain Wisdom. Wisdom was earned later from the visible level 9, 12, and 27 choices after 447 visible campaign Tactical Duels had been settled through the battlefield result card.

The campaign reached level 27 with Wisdom 3. Reload preserved level, XP, Wisdom rank, all ten resolved offer choices, and mana. The Spellbook exposed Resurrection with its accessible description, “Resurrection. Restores 50×Power HP of losses Mana 20.” The 1280×720 capture shows all eight spell cards over the campaign map.

## Natural casualty and restoration

After reloading at Wisdom 3, the player traveled by visible routes to the unresolved Jade Karst guard at (6, 6), route cost 3. Its visible encounter contained Bandits ×7 and Dire Wolves ×8. In the resulting Tactical battle, a Clubman casualty reduced the natural army stack from 12/12 to 11/12.

Visible Resurrection spent 20 mana (150 → 130), restored the living stack from 11/12 to 12/12, and logged the resurrect spell against that stack. Reload retained the spell event, 130 mana, and the restored 12/12 count. The battle was then finished with visible Auto and settlement controls; the campaign army remained at 12 and guard (6, 6) was recorded as resolved. No battle state or casualty count was injected.

I reviewed the saved 1280×720 Spellbook and post-cast Tactical captures. Evidence: [full natural-run report](m21-natural-wisdom3-resurrection-live-20261021-run09/report.json), [Spellbook capture](m21-natural-wisdom3-resurrection-live-20261021-run09/earned-wisdom3-spellbook.png), and [post-cast Tactical capture](m21-natural-wisdom3-resurrection-live-20261021-run09/natural-resurrection-cast.png). The run passed with zero browser errors.

Earlier runs remain useful history: run05 proved an HP heal without a casualty; run06–run08 did not close the casualty requirement and some did not reach Wisdom 3 within their chosen cap. Run09 supersedes those runs for this bounded Resurrection gate.

## All-eight natural cast coverage — run02

Run02 was another fresh Mage campaign with no saved or injected state. The player reached Wisdom 3 by visible skill offers at level 21 after 268 settled Tactical Duels, spent earned attribute points on Knowledge through the visible Hero controls, and reloaded. The Spellbook displayed the learned spells. The player then cast each spell through visible Tactical choices, reloaded after every cast, and verified its event, mana cost and effect:

- Magic Arrow, Lightning Bolt and Fireball changed enemy stacks.
- Bless, Haste and Slow applied their corresponding stack counters.
- Cure spent 6 mana and healed a natural guard casualty from 11/12 to 12/12.
- Resurrection spent 20 mana and restored a later natural casualty from 11/12 to 12/12.

The six Tactical Duel spell battles won and settled visibly. The final Adventure guard was lost after the spell casts while the runner used repeated Defend actions to expose healing targets. Its runner exit is therefore a failed full-battle continuation, not a spell-cast failure. The separate run09 guard battle won and settled after Resurrection. The [run02 leaf audit](m21-natural-all-spells-live-20261021-run02/spell-leaf-audit.json) checks every spell's effect, exact mana cost, log event and reload state against the full report; the visual contact sheet shows the captured cast states. Evidence: [run02 report](m21-natural-all-spells-live-20261021-run02/report.json), [cast contact sheet](m21-natural-all-spells-live-20261021-run02/natural-spell-cast-contact-sheet.jpg), [run02 runner](m21-natural-all-spells-live-20261021-run02.mjs).

The earlier run01 is retained as a failed natural progression attempt: it lost at duel 315 with Wisdom 2, mana 0 and no surviving army, before any spell casts. The revised visible progression choices and Knowledge spending in run02 reached Wisdom 3 and completed the spell observations.

## Acceptance status

- Wisdom 3 through visible offers and reload: **bounded PASS**.
- Resurrection access, natural in-battle casualty restoration, mana cost, spell event, restored count, reload persistence, and battle settlement: **bounded PASS**.
- All eight spells cast through natural progression with observed effects and persistence: **bounded PASS**; the run02 final guard battle itself ended in defeat after the casts.
- Complete M21 mock acceptance, all 30 screen mocks, all 18 journeys, all 32 age/mode scenes, independent desktop review, final APK, device checks, and owner acceptance: **OPEN**.

This browser run does not upgrade the M21 feature to complete or change the whole-game status.
