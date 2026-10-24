# Spellbook and Tactical action layout repair — 20 October 2026

**Focused repair: PASS. Whole-game acceptance remains INCOMPLETE.**

## Findings and changes

At short landscape heights, the Hero panel close control floated beside its content and narrowed the Spellbook grid by about 56 px. On 825×375 this clipped the second spell row; at 933×424 some names wrapped poorly. The Hero detail grid now clears the close-control float. Short-height card sizing shows both rows without scrolling, and long spell names can wrap inside their cards.

In Tactical, choosing Spell opened the detail panel. The action renderer assumed its action buttons had been copied to the dock, but the shared button helper suppresses dock copies while a panel is open. The missing dock node caused a null access and prevented cast targets from rendering. Tactical now always creates its action medallions directly in the dock, which stays visible beside the open target panel.

## Verification

- Fresh natural Warlock journeys at 825×375 and 1280×720: start campaign, build Barracks, recruit five Melee, route to and enter a guard battle, cast Magic Arrow, make a manual move, auto-resolve the remaining battle, settle victory, and reload. Mana changed from 30 to 25; the battle log records the cast; the post-battle roster persists. Both runs report zero page/console errors and zero missing requests.
- Fresh Warlock Spellbook UI at 825×375, 933×424, 1180×820, and 1280×720: all eight cards fit in the panel; all centers resolve to their intended button; labels fit within their text boxes; no page/console or HTTP 4xx errors.
- Fresh all-surface sweep after the changes: 116 captures across the four landscape sizes, zero page/console errors, and zero fully exposed control hit failures.
- Fresh Node regression suite: 211/211 pass, including the long save-stress test.
- Reviewed current Spellbook captures: [825×375](spellbook-responsive-live/hero-spellbook-825x375.png), [933×424](spellbook-responsive-live/hero-spellbook-933x424.png), and [1280×720](../surfaces/hero-spellbook-1280x720.png). Full geometry report: [Spellbook layout report](spellbook-responsive-live/report.json). The two natural battle reports are in [825×375](natural-spell-cast-warlock-825x375/report.json) and [1280×720](natural-spell-cast-warlock-1280x720/report.json).

## Remaining acceptance

These targeted repairs do not close M01–M30, J01–J18, all 32 physical scene traces, complete all-age class/kit/motion coverage, independent desktop acceptance, the final snapshot APK, or later device and owner gates. No APK, device, release, paid provider, or owner-acceptance action occurred.
