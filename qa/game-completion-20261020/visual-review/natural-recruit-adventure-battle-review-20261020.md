# Natural recruitment, spell, Adventure and battle review — 20 October 2026

**Result: bounded natural UI journeys pass; game acceptance remains INCOMPLETE.** Each run used a new isolated Chromium profile and real screen controls, without importing a campaign or injecting game state/resources.

## Journeys

- Knight campaign at 1280×720, 825×375 and 933×424: build a Barracks, recruit five Melee, leave town, preview and confirm a legal route, meet the guard at the route destination, move an allied formation through the Tactical UI, auto-resolve the remainder, settle victory, wait for the durable save acknowledgement, reload, and compare the saved roster with the settled result.
- Warlock campaign at 825×375: inspect the accessible Spellbook, cast Magic Arrow against a live guard in Tactical, verify mana dropped from 30 to 25 and the combat log records the Arrow cast, then perform a manual move, settle the encounter and reload.

The Knight runs won the encounter with no open battle after settlement; the post-battle roster, including casualties, survived reload. All five runs reported zero page/console errors and zero 404 requests. The current browser runner is `natural-recruit-adventure-battle-journey-20261020.mjs`; per-run JSON reports are beside the captures in the matching `natural-recruit-adventure-battle*` and `natural-spell-cast-warlock-825x375` folders.

## Visual review

- Army, Adventure, Tactical, battle result, reload and Warlock Spellbook screens were inspected at the captured landscape sizes. The Army roster and Tactical destination list use the scrollable inspector; accessible controls remained actionable at both phone widths.
- The mounted hero reached the selected encounter cell after its travel animation. Movement and spell changes were visible in the live scene, and the result card provided the return-to-campaign control.
- The diagonal Kingdom plot axes are intentional: the active transform uses two diagonal world basis vectors and the same oblique camera as the approved landscape mock. Runtime building images use measured foot anchors without per-building rotation.
- The assembled Kingdom still falls short of the approved mock set in settlement density and integrated wall/plot appearance. Those visual gaps remain open, as do full mock-by-mock and journey coverage, the remaining scene traces, independent desktop acceptance, and exact final APK verification.

## Bounded automated checks

Fresh `node --test tests/*.test.mjs`: **209/209 passed**, including the 10,000-command save-stress horizon. This is Node evidence, not visual acceptance, full natural-play coverage, device verification or owner acceptance. No game source changed in this review; work was limited to QA script, captures and report.
