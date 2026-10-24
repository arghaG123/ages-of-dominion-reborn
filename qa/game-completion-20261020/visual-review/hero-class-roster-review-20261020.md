# Hero class roster live repair and review — 20 October 2026

**Focused interaction and layout result: PASS; art/mock acceptance remains OPEN; whole game remains INCOMPLETE.**

## Scope and results

Used three fresh isolated browser profiles at 825×375, 933×424 and 1280×720. Each profile started a new campaign through the UI, showed all eight class cards, selected Knight, Ranger, Warlock, Mage, Paladin, Barbarian, Necromancer and Healer in turn, then entered the valley. The final Healer selection carried into Kingdom and `enteredValley` persisted. All 24 class selections, card centers and valley-entry actions passed; all eight portrait images loaded at each size. No page errors, failed responses or document overflow occurred.

Screenshots: [825×375](hero-class-roster-live/hero-class-roster-825x375.png), [933×424](hero-class-roster-live/hero-class-roster-933x424.png), [1280×720](hero-class-roster-live/hero-class-roster-1280x720.png). Machine evidence: [three-run report](hero-class-roster-live/report.json) and [browser runner](hero-class-roster-live-20261020.mjs).

## Visual review

- The large central hero and stone hall form a clear selection scene, and the eight class cards remain visible and clickable at all three sizes. The valley-entry action also remains in-frame.
- Class names now appear beside the portrait on all eight cards, including the compact landscape view. Cards use a consistent square thumbnail frame and retain the accessible class name on the semantic button.
- Knight still uses the era-appropriate standing-body fallback because its ancient square portrait remains pending review; the later Medieval portrait stays age-gated. The card no longer has a unique layout, but exact portrait-source parity remains open.
- All cards retain at least 48×48 CSS-pixel hit areas, center hits, visible selected state and unobstructed valley entry at each size.
- The approved 30-mock set has no dedicated new-campaign class-selection screen. Mock 19 guides the Hero equipment scene; it is not direct pixel-parity evidence for this initial roster. This review therefore establishes functional layout and art loading only.

## Acceptance boundary

This is an isolated fresh-campaign UI check, not a full class-by-class gameplay, equipment, spell, battle, natural-age progression or owner-acceptance run. The compact visible-name gap is repaired; exact portrait-source parity, the full M01–M30/J01–J18 scope, independent desktop review, final snapshot APK, later device and owner gates remain open. No new art was generated or bound.
