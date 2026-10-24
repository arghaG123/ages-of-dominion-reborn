# M21 Spellbook mock comparison — 20 October 2026

**Result: eight-spell presentation and compact selected-spell feedback PASS at the inspected viewports; full mock fidelity remains PARTIAL.**

## Evidence inspected

- Approved M21 target: design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/21-spells.jpg (1360×768).
- Initial runtime views: qa/game-completion-20261020/visual-review/core-screens-live-20261020/hero-spellbook-825x375.png and hero-spellbook-1280x720.png.
- Compact scroll view: hero-spellbook-scrolled-825x375.png.
- Selected Magic Arrow: hero-spell-detail-compact-825x375.png and hero-spell-detail-1280x720.png.
- Core isolated browser runner was freshly rerun and passed 12 screens at each of 825×375 and 1280×720, with all terrain images loaded and zero browser errors/failed responses. Spellbook captures and selection used additional fresh contexts and visible UI controls.
- Focused feedback repair runner: `qa/game-completion-20261020/visual-review/m21-spellbook-feedback-live-20261020.mjs`; results and selected-state captures: `qa/game-completion-20261020/visual-review/m21-spellbook-feedback-live-20261020/`.

## Comparison and live interaction

The approved mock shows the spellbook and Cast action over a wide adventure landscape, alongside hero/resource context. The current screen shows the complete Hero figure in a material chamber with the spellbook in a right-side panel. Its eight icon cards are legible at both inspected sizes. At fresh Stone/Wisdom 0, Magic Arrow, Bless, Haste and Cure are available; Slow and Lightning Bolt require Wisdom 1, Fireball Wisdom 2, and Resurrection Wisdom 3. The rendered cards show their names, mana costs and lock badges; their accessible labels also state effects and exact Wisdom requirements.

Clicking Magic Arrow through the live Warlock UI now updates the Spellbook header with “Magic Arrow · 10 + 10×Power damage · Effect 40 · 5 mana” and highlights the selected card. The detail stays inside the viewport at 825×375 (y=152–183) and 1280×720 (y=187–229). The live mana total remains 30/30, confirming selection does not spend mana. All eight cards remain in-frame at both sizes after selection; locked spells retain their Wisdom badges.

## Acceptance status

- Eight distinct spell cards with names, mana costs and Wisdom lock states: observed at both viewports.
- Magic Arrow selection detail and no-spend-on-selection: observed in a fresh UI journey.
- Compact selected-spell feedback: **PASS**; effect, computed amount and mana cost are visible without scrolling at 825×375 and 1280×720.
- M21 composition across Hero detail and Tactical casting: **PARTIAL / OPEN**. The approved mock places spells and Cast over the game field; the inspected Hero tab is a separate chamber view. A natural Magic Arrow battle cast is verified separately, but the integrated mock composition is not.
- Natural tactical Magic Arrow cast, manual move, victory settlement and reload: bounded PASS in the same-day Warlock journeys at 825×375 and 1280×720; mana changed 30→25 and the battle log recorded the cast. These reports were reviewed, not rerun in this screen review: qa/game-completion-20261020/visual-review/natural-spell-cast-warlock-825x375/report.json and qa/game-completion-20261020/visual-review/natural-spell-cast-warlock-1280x720/report.json.
- Other spell effects, target legality, Wisdom 3 Resurrection outcome, cancellation and complete spell persistence coverage: **OPEN**.
- Overall M21 mock fidelity and whole-game acceptance: **OPEN**.

The feedback repair is in `src/client/main.js` and `src/client/polish.css`. Fresh natural Spellbook UI runs at 825×375 and 1280×720 passed with zero browser/console errors or failed responses. The full Node suite passes 228/228 after this repair. This is a bounded visual/runtime repair, not M21 or whole-game acceptance; the approved adventure-scene composition, other spell targets/effects, Wisdom 3 Resurrection outcome, cancellation and complete persistence coverage remain open. No image provider, package, device or owner-review action occurred.
